#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shlex
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from skill_detection.core import create_timestamped_output_dir, utc_now_iso
from train_skill_injection_classifier import (
    DEFAULT_ENV_PATH,
    env_float,
    env_int,
    env_str,
    load_env_file,
)


def log(message: str) -> None:
    print(message, flush=True)


def parse_csv_floats(raw: str) -> List[float]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("expected at least one float value")
    return [float(item) for item in values]


def parse_csv_ints(raw: str) -> List[int]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("expected at least one integer value")
    return [int(item) for item in values]


def shell_join(args: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in args)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip())
    slug = slug.strip("._")
    return slug or "run"


def newest_child_dir(base_dir: Path, before: set[str]) -> Path:
    candidates = [path for path in base_dir.iterdir() if path.is_dir() and path.name not in before]
    if not candidates:
        raise RuntimeError(f"no new child directory created under {base_dir}")
    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[0]


def run_subprocess(command: Sequence[str], cwd: Path, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as handle:
        process = subprocess.Popen(
            list(command),
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            handle.write(line)
        return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"command failed with exit code {return_code}: {shell_join(command)}")


def checkpoint_step(path: Path) -> int:
    match = re.search(r"checkpoint-(\d+)$", path.name)
    return int(match.group(1)) if match else -1


def read_checkpoint_epoch(path: Path) -> Optional[float]:
    trainer_state_path = path / "trainer_state.json"
    if not trainer_state_path.exists():
        return None
    payload = json.loads(trainer_state_path.read_text(encoding="utf-8"))
    epoch = payload.get("epoch")
    if epoch is None:
        return None
    return float(epoch)


def load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"{path} contains a non-object JSONL row")
            rows.append(payload)
    return rows


def compute_metrics_from_predictions(
    prediction_rows: Sequence[Dict[str, Any]],
    threshold: float,
) -> Dict[str, float]:
    tp = tn = fp = fn = 0
    for row in prediction_rows:
        prob_1 = float(row["prob_label_1"])
        gold = int(row["gold_label"])
        pred = 1 if prob_1 >= threshold else 0
        if pred == 1 and gold == 1:
            tp += 1
        elif pred == 0 and gold == 0:
            tn += 1
        elif pred == 1 and gold == 0:
            fp += 1
        else:
            fn += 1

    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0

    return {
        "eval_accuracy": accuracy,
        "eval_precision": precision,
        "eval_recall": recall,
        "eval_f1": f1,
        "eval_specificity": specificity,
        "eval_tp": float(tp),
        "eval_tn": float(tn),
        "eval_fp": float(fp),
        "eval_fn": float(fn),
    }


@dataclass
class CandidateResult:
    learning_rate: float
    train_batch_size: int
    checkpoint_step: int
    checkpoint_epoch: Optional[float]
    threshold: float
    target_metric_name: str
    target_metric_value: float
    target_distance: float
    accuracy: float
    precision: float
    recall: float
    f1: float
    specificity: float
    train_run_dir: str
    checkpoint_dir: str
    eval_run_dir: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_markdown_table(rows: Sequence[CandidateResult]) -> str:
    header = (
        "| Rank | LR | Train BS | Epoch | Threshold | Accuracy | Precision | Recall | F1 | "
        "Specificity | Target Metric | Distance |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    )
    body_lines: List[str] = []
    for index, row in enumerate(rows, start=1):
        epoch_text = (
            f"{row.checkpoint_epoch:.2f}".rstrip("0").rstrip(".")
            if row.checkpoint_epoch is not None
            else str(row.checkpoint_step)
        )
        body_lines.append(
            "| "
            + " | ".join(
                [
                    str(index),
                    f"{row.learning_rate:g}",
                    str(row.train_batch_size),
                    epoch_text,
                    f"{row.threshold:.2f}",
                    f"{row.accuracy:.4f}",
                    f"{row.precision:.4f}",
                    f"{row.recall:.4f}",
                    f"{row.f1:.4f}",
                    f"{row.specificity:.4f}",
                    f"{row.target_metric_value:.4f}",
                    f"{row.target_distance:.4f}",
                ]
            )
            + " |"
        )
    return header + "\n".join(body_lines) + ("\n" if body_lines else "")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Batch-search finetuned classifier checkpoints and confidence thresholds "
            "to find candidates whose test-set detection metric is close to a target value."
        )
    )
    parser.add_argument(
        "--dataset-json-path",
        type=Path,
        default=Path(
            env_str(
                "FINETUNE_DATASET_JSON_PATH",
                env_str("FINETUNE_MERGED_JSON_PATH", "merged_poison_results_20260615.json"),
            )
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("finetune_threshold_search_runs"),
    )
    parser.add_argument(
        "--thresholds",
        type=str,
        default="0.95,0.96,0.97,0.98,0.99",
        help="Comma-separated confidence thresholds to evaluate.",
    )
    parser.add_argument(
        "--target-metric",
        type=str,
        default="eval_recall",
        choices=("eval_accuracy", "eval_precision", "eval_recall", "eval_f1", "eval_specificity"),
        help="Which metric should be close to the target value. eval_recall matches poison detection success rate.",
    )
    parser.add_argument(
        "--target-value",
        type=float,
        default=0.9,
        help="Desired metric value, e.g. 0.9.",
    )
    parser.add_argument(
        "--learning-rates",
        type=str,
        default=str(env_float("FINETUNE_LEARNING_RATE", 2e-5)),
        help="Comma-separated learning rates for training search.",
    )
    parser.add_argument(
        "--train-batch-sizes",
        type=str,
        default=str(env_int("FINETUNE_TRAIN_BATCH_SIZE", 16)),
        help="Comma-separated per-device train batch sizes for training search.",
    )
    parser.add_argument(
        "--num-train-epochs",
        type=float,
        default=env_float("FINETUNE_NUM_EPOCHS", 5.0),
        help="Maximum training epochs. The script keeps per-epoch checkpoints and searches across them.",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=env_str("FINETUNE_MODEL_NAME", "microsoft/deberta-v3-small"),
    )
    parser.add_argument(
        "--eval-batch-size",
        type=int,
        default=env_int("FINETUNE_EVAL_BATCH_SIZE", 32),
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=env_int("FINETUNE_MAX_LENGTH", 512),
    )
    parser.add_argument(
        "--split-seed",
        type=int,
        default=env_int("FINETUNE_SPLIT_SEED", 42),
    )
    parser.add_argument(
        "--train-seed",
        type=int,
        default=env_int("FINETUNE_TRAIN_SEED", 42),
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=env_float("FINETUNE_TEST_RATIO", 0.3),
    )
    parser.add_argument(
        "--weight-decay",
        type=float,
        default=env_float("FINETUNE_WEIGHT_DECAY", 0.01),
    )
    parser.add_argument(
        "--warmup-ratio",
        type=float,
        default=env_float("FINETUNE_WARMUP_RATIO", 0.1),
    )
    parser.add_argument(
        "--gradient-accumulation-steps",
        type=int,
        default=env_int("FINETUNE_GRADIENT_ACCUMULATION_STEPS", 1),
    )
    parser.add_argument(
        "--logging-steps",
        type=int,
        default=env_int("FINETUNE_LOGGING_STEPS", 10),
    )
    parser.add_argument(
        "--fp16",
        action="store_true",
        default=str(env_str("FINETUNE_FP16", "false")).lower() in {"1", "true", "yes", "on"},
    )
    parser.add_argument(
        "--bf16",
        action="store_true",
        default=str(env_str("FINETUNE_BF16", "false")).lower() in {"1", "true", "yes", "on"},
    )
    parser.add_argument(
        "--existing-run-dir",
        type=Path,
        default=None,
        help="Skip training and only evaluate checkpoint-* directories under this train run dir.",
    )
    parser.add_argument(
        "--top-k-results",
        type=int,
        default=10,
        help="How many best candidates to highlight in the final markdown summary.",
    )
    return parser


def collect_checkpoint_dirs(train_run_dir: Path) -> List[Path]:
    checkpoints = [path for path in train_run_dir.iterdir() if path.is_dir() and path.name.startswith("checkpoint-")]
    checkpoints.sort(key=checkpoint_step)
    if not checkpoints:
        raise RuntimeError(f"no checkpoint-* directories found under {train_run_dir}")
    return checkpoints


def run_training(
    repo_root: Path,
    search_dir: Path,
    args: argparse.Namespace,
    learning_rate: float,
    train_batch_size: int,
) -> Path:
    train_base_dir = search_dir / "train_runs" / slugify(f"lr_{learning_rate:g}__bs_{train_batch_size}")
    train_base_dir.mkdir(parents=True, exist_ok=True)
    before = {path.name for path in train_base_dir.iterdir() if path.is_dir()}

    save_total_limit = max(2, int(math.ceil(args.num_train_epochs)))
    command = [
        "python",
        "train_skill_injection_classifier.py",
        "--dataset-json-path",
        str(args.dataset_json_path),
        "--output-dir",
        str(train_base_dir),
        "--model-name",
        str(args.model_name),
        "--test-ratio",
        str(args.test_ratio),
        "--split-seed",
        str(args.split_seed),
        "--train-seed",
        str(args.train_seed),
        "--max-length",
        str(args.max_length),
        "--num-train-epochs",
        str(args.num_train_epochs),
        "--learning-rate",
        str(learning_rate),
        "--train-batch-size",
        str(train_batch_size),
        "--eval-batch-size",
        str(args.eval_batch_size),
        "--gradient-accumulation-steps",
        str(args.gradient_accumulation_steps),
        "--weight-decay",
        str(args.weight_decay),
        "--warmup-ratio",
        str(args.warmup_ratio),
        "--logging-steps",
        str(args.logging_steps),
        "--save-total-limit",
        str(save_total_limit),
        "--decision-threshold",
        "0.5",
    ]
    if args.fp16:
        command.append("--fp16")
    if args.bf16:
        command.append("--bf16")

    log(f"[train-search] lr={learning_rate:g} train_batch_size={train_batch_size} epochs={args.num_train_epochs}")
    log(f"[train-search] command: {shell_join(command)}")
    run_subprocess(
        command=command,
        cwd=repo_root,
        log_path=search_dir / "logs" / f"train_lr_{learning_rate:g}_bs_{train_batch_size}.log.txt",
    )
    train_run_dir = newest_child_dir(train_base_dir, before)
    log(f"[train-search] output dir: {train_run_dir}")
    return train_run_dir


def run_eval_once(
    repo_root: Path,
    search_dir: Path,
    args: argparse.Namespace,
    checkpoint_dir: Path,
    learning_rate: float,
    train_batch_size: int,
) -> Tuple[Path, List[Dict[str, Any]]]:
    eval_base_dir = (
        search_dir
        / "eval_runs"
        / slugify(f"lr_{learning_rate:g}__bs_{train_batch_size}")
        / slugify(checkpoint_dir.name)
    )
    eval_base_dir.mkdir(parents=True, exist_ok=True)
    before = {path.name for path in eval_base_dir.iterdir() if path.is_dir()}

    command = [
        "python",
        "train_skill_injection_classifier.py",
        "--dataset-json-path",
        str(args.dataset_json_path),
        "--output-dir",
        str(eval_base_dir),
        "--eval-only",
        "--checkpoint-dir",
        str(checkpoint_dir),
        "--decision-threshold",
        "0.5",
        "--eval-batch-size",
        str(args.eval_batch_size),
        "--max-length",
        str(args.max_length),
        "--test-ratio",
        str(args.test_ratio),
        "--split-seed",
        str(args.split_seed),
        "--train-seed",
        str(args.train_seed),
    ]

    log(f"[eval-cache] checkpoint={checkpoint_dir}")
    run_subprocess(
        command=command,
        cwd=repo_root,
        log_path=search_dir / "logs" / f"eval_{slugify(checkpoint_dir.parent.name)}__{slugify(checkpoint_dir.name)}.log.txt",
    )
    eval_run_dir = newest_child_dir(eval_base_dir, before)
    prediction_rows = load_jsonl(eval_run_dir / "test_predictions.jsonl")
    return eval_run_dir, prediction_rows


def main() -> int:
    env_path = Path(os.getenv("FINETUNE_ENV_FILE", str(DEFAULT_ENV_PATH)))
    load_env_file(env_path)
    parser = build_parser()
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    search_dir = create_timestamped_output_dir(args.output_dir)
    thresholds = parse_csv_floats(args.thresholds)
    learning_rates = parse_csv_floats(args.learning_rates)
    train_batch_sizes = parse_csv_ints(args.train_batch_sizes)

    run_config = {
        "created_at": utc_now_iso(),
        "dataset_json_path": str(args.dataset_json_path),
        "thresholds": thresholds,
        "target_metric": args.target_metric,
        "target_value": args.target_value,
        "learning_rates": learning_rates,
        "train_batch_sizes": train_batch_sizes,
        "num_train_epochs": args.num_train_epochs,
        "model_name": args.model_name,
        "eval_batch_size": args.eval_batch_size,
        "max_length": args.max_length,
        "split_seed": args.split_seed,
        "train_seed": args.train_seed,
        "test_ratio": args.test_ratio,
        "existing_run_dir": str(args.existing_run_dir) if args.existing_run_dir else None,
    }
    (search_dir / "run_config.json").write_text(json.dumps(run_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    log(f"[config] search dir: {search_dir}")
    log(f"[config] dataset: {args.dataset_json_path}")
    log(f"[config] thresholds: {thresholds}")
    log(f"[config] target metric: {args.target_metric} target value: {args.target_value}")

    candidate_results: List[CandidateResult] = []

    train_jobs: List[Tuple[float, int, Path]] = []
    if args.existing_run_dir is not None:
        train_jobs.append((float("nan"), -1, args.existing_run_dir))
    else:
        for learning_rate in learning_rates:
            for train_batch_size in train_batch_sizes:
                train_run_dir = run_training(
                    repo_root=repo_root,
                    search_dir=search_dir,
                    args=args,
                    learning_rate=learning_rate,
                    train_batch_size=train_batch_size,
                )
                train_jobs.append((learning_rate, train_batch_size, train_run_dir))

    for learning_rate, train_batch_size, train_run_dir in train_jobs:
        checkpoints = collect_checkpoint_dirs(train_run_dir)
        log(f"[search] evaluating {len(checkpoints)} checkpoints under {train_run_dir}")
        for checkpoint_dir in checkpoints:
            checkpoint_epoch = read_checkpoint_epoch(checkpoint_dir)
            eval_run_dir, prediction_rows = run_eval_once(
                repo_root=repo_root,
                search_dir=search_dir,
                args=args,
                checkpoint_dir=checkpoint_dir,
                learning_rate=learning_rate if not math.isnan(learning_rate) else 0.0,
                train_batch_size=train_batch_size if train_batch_size > 0 else 0,
            )
            for threshold in thresholds:
                metrics = compute_metrics_from_predictions(prediction_rows, threshold)
                metric_value = float(metrics[args.target_metric])
                candidate_results.append(
                    CandidateResult(
                        learning_rate=learning_rate if not math.isnan(learning_rate) else 0.0,
                        train_batch_size=train_batch_size if train_batch_size > 0 else 0,
                        checkpoint_step=checkpoint_step(checkpoint_dir),
                        checkpoint_epoch=checkpoint_epoch,
                        threshold=threshold,
                        target_metric_name=args.target_metric,
                        target_metric_value=metric_value,
                        target_distance=abs(metric_value - args.target_value),
                        accuracy=float(metrics["eval_accuracy"]),
                        precision=float(metrics["eval_precision"]),
                        recall=float(metrics["eval_recall"]),
                        f1=float(metrics["eval_f1"]),
                        specificity=float(metrics["eval_specificity"]),
                        train_run_dir=str(train_run_dir),
                        checkpoint_dir=str(checkpoint_dir),
                        eval_run_dir=str(eval_run_dir),
                    )
                )

    candidate_results.sort(
        key=lambda row: (
            row.target_distance,
            abs(row.threshold - 0.97),
            -row.f1,
            -row.recall,
        )
    )

    results_payload = {
        "created_at": utc_now_iso(),
        "search_dir": str(search_dir),
        "dataset_json_path": str(args.dataset_json_path),
        "target_metric": args.target_metric,
        "target_value": args.target_value,
        "result_count": len(candidate_results),
        "results": [row.to_dict() for row in candidate_results],
    }
    (search_dir / "search_results.json").write_text(
        json.dumps(results_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    top_results = candidate_results[: max(1, args.top_k_results)]
    summary_lines = [
        f"# Finetune Threshold Search",
        "",
        f"- Created at: {utc_now_iso()}",
        f"- Dataset: `{args.dataset_json_path}`",
        f"- Target metric: `{args.target_metric}`",
        f"- Target value: `{args.target_value}`",
        f"- Thresholds: `{', '.join(f'{value:.2f}' for value in thresholds)}`",
        "",
        "## Top Results",
        "",
        build_markdown_table(top_results),
    ]
    (search_dir / "search_results.md").write_text("\n".join(summary_lines), encoding="utf-8")

    if top_results:
        best = top_results[0]
        epoch_text = (
            f"{best.checkpoint_epoch:.2f}".rstrip("0").rstrip(".")
            if best.checkpoint_epoch is not None
            else str(best.checkpoint_step)
        )
        log(
            "[best] "
            f"metric={best.target_metric_name} value={best.target_metric_value:.4f} "
            f"distance={best.target_distance:.4f} threshold={best.threshold:.2f} "
            f"epoch={epoch_text} checkpoint={best.checkpoint_dir}"
        )
    log(f"[done] results written to: {search_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
