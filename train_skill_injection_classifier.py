#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from skill_detection.core import (
    atomic_write_json,
    discover_skills,
    discover_skills_from_json,
    split_skill_records,
    utc_now_iso,
)


DEFAULT_ENV_PATH = Path(".env")
DEFAULT_CLEAN_ROOT = Path("openaclaw_samples/clean")
DEFAULT_POISON_JSON_PATH = Path("skill_poison_results_sum.json")
DEFAULT_OUTPUT_DIR = Path("finetune_runs/deberta_v3_small")

MODEL_ALIASES = {
    "deberta-v3-small": "microsoft/deberta-v3-small",
    "deberta-v3-large": "microsoft/deberta-v3-large",
}


def log(message: str) -> None:
    print(message, flush=True)


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value and value[0] in {"'", '"'} and value[-1] == value[0]:
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        os.environ.setdefault(key, value)


def env_str(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def env_int(name: str, default: Optional[int] = None) -> Optional[int]:
    value = env_str(name)
    if value is None:
        return default
    return int(value)


def env_float(name: str, default: Optional[float] = None) -> Optional[float]:
    value = env_str(name)
    if value is None:
        return default
    return float(value)


def env_bool(name: str, default: bool = False) -> bool:
    value = env_str(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "y", "on"}


@dataclass
class ClassificationExample:
    example_id: str
    text: str
    label: int
    source_dataset: str
    split: str
    skill_name: str
    description: str
    trigger_text: Optional[str]
    skill_key: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Fine-tune a DeBERTa-v3 binary classifier for skill prompt-injection "
            "detection using clean skills and poisoned JSON skills."
        )
    )
    parser.add_argument(
        "--clean-root",
        type=Path,
        default=Path(env_str("FINETUNE_CLEAN_ROOT", str(DEFAULT_CLEAN_ROOT))),
    )
    parser.add_argument(
        "--poison-json-path",
        type=Path,
        default=Path(env_str("FINETUNE_POISON_JSON_PATH", str(DEFAULT_POISON_JSON_PATH))),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(env_str("FINETUNE_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR))),
    )
    parser.add_argument(
        "--model-name",
        default=env_str("FINETUNE_MODEL_NAME", MODEL_ALIASES["deberta-v3-small"]),
        help="Model name or path. Recommended: microsoft/deberta-v3-small or microsoft/deberta-v3-large.",
    )
    parser.add_argument(
        "--clean-test-ratio",
        type=float,
        default=env_float("FINETUNE_CLEAN_TEST_RATIO", 0.3),
    )
    parser.add_argument(
        "--poison-test-ratio",
        type=float,
        default=env_float("FINETUNE_POISON_TEST_RATIO", 0.3),
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
        "--max-length",
        type=int,
        default=env_int("FINETUNE_MAX_LENGTH", 512),
    )
    parser.add_argument(
        "--num-train-epochs",
        type=float,
        default=env_float("FINETUNE_NUM_EPOCHS", 5.0),
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=env_float("FINETUNE_LEARNING_RATE", 2e-5),
    )
    parser.add_argument(
        "--train-batch-size",
        type=int,
        default=env_int("FINETUNE_TRAIN_BATCH_SIZE", 16),
    )
    parser.add_argument(
        "--eval-batch-size",
        type=int,
        default=env_int("FINETUNE_EVAL_BATCH_SIZE", 32),
    )
    parser.add_argument(
        "--gradient-accumulation-steps",
        type=int,
        default=env_int("FINETUNE_GRADIENT_ACCUMULATION_STEPS", 1),
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
        "--logging-steps",
        type=int,
        default=env_int("FINETUNE_LOGGING_STEPS", 10),
    )
    parser.add_argument(
        "--save-total-limit",
        type=int,
        default=env_int("FINETUNE_SAVE_TOTAL_LIMIT", 2),
    )
    parser.add_argument(
        "--metric-for-best-model",
        default=env_str("FINETUNE_METRIC_FOR_BEST_MODEL", "f1"),
    )
    parser.add_argument(
        "--greater-is-better",
        action="store_true",
        default=env_bool("FINETUNE_GREATER_IS_BETTER", True),
    )
    parser.add_argument(
        "--no-greater-is-better",
        action="store_false",
        dest="greater_is_better",
    )
    parser.add_argument(
        "--fp16",
        action="store_true",
        default=env_bool("FINETUNE_FP16", False),
    )
    parser.add_argument(
        "--bf16",
        action="store_true",
        default=env_bool("FINETUNE_BF16", False),
    )
    parser.add_argument(
        "--eval-only",
        action="store_true",
        default=env_bool("FINETUNE_EVAL_ONLY", False),
        help="Skip training and only evaluate a saved checkpoint.",
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=Path(env_str("FINETUNE_CHECKPOINT_DIR")) if env_str("FINETUNE_CHECKPOINT_DIR") else None,
        help="Checkpoint directory used by --eval-only.",
    )
    return parser


def seed_everything(seed: int) -> None:
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


def shuffle_examples(examples: Sequence[ClassificationExample], seed: int) -> List[ClassificationExample]:
    items = list(examples)
    rng = random.Random(seed)
    rng.shuffle(items)
    return items


def build_examples(clean_records: Sequence[Any], poison_records: Sequence[Any], split_name: str) -> List[ClassificationExample]:
    examples: List[ClassificationExample] = []

    for record in clean_records:
        examples.append(
            ClassificationExample(
                example_id=f"clean::{record.skill_key}",
                text=record.input_text,
                label=0,
                source_dataset=record.source_dataset,
                split=split_name,
                skill_name=record.skill_name,
                description=record.description,
                trigger_text=record.trigger_text,
                skill_key=record.skill_key,
            )
        )

    for record in poison_records:
        examples.append(
            ClassificationExample(
                example_id=f"poison::{record.skill_key}",
                text=record.input_text,
                label=1,
                source_dataset=record.source_dataset,
                split=split_name,
                skill_name=record.skill_name,
                description=record.description,
                trigger_text=record.trigger_text,
                skill_key=record.skill_key,
            )
        )

    return examples


def to_hf_dataset(examples: Sequence[ClassificationExample]) -> Any:
    from datasets import Dataset

    rows = [example.to_dict() for example in examples]
    return Dataset.from_list(rows)


def compute_metrics_builder() -> Any:
    import numpy as np

    def compute_metrics(eval_pred: Any) -> Dict[str, float]:
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        labels = np.asarray(labels)
        predictions = np.asarray(predictions)

        accuracy = float((predictions == labels).mean())
        tp = int(((predictions == 1) & (labels == 1)).sum())
        tn = int(((predictions == 0) & (labels == 0)).sum())
        fp = int(((predictions == 1) & (labels == 0)).sum())
        fn = int(((predictions == 0) & (labels == 1)).sum())

        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall)
            else 0.0
        )
        specificity = tn / (tn + fp) if (tn + fp) else 0.0

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "specificity": specificity,
            "tp": float(tp),
            "tn": float(tn),
            "fp": float(fp),
            "fn": float(fn),
        }

    return compute_metrics


def resolve_model_name(raw_model_name: str) -> str:
    return MODEL_ALIASES.get(raw_model_name, raw_model_name)


def infer_run_name(model_name: str) -> str:
    safe = model_name.replace("/", "__")
    return safe


def build_training_arguments(args: argparse.Namespace, output_dir: Path) -> Any:
    from transformers import TrainingArguments

    return TrainingArguments(
        output_dir=str(output_dir),
        overwrite_output_dir=True,
        do_train=not args.eval_only,
        do_eval=True,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=args.logging_steps,
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.train_batch_size,
        per_device_eval_batch_size=args.eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        num_train_epochs=args.num_train_epochs,
        weight_decay=args.weight_decay,
        warmup_ratio=args.warmup_ratio,
        load_best_model_at_end=not args.eval_only,
        metric_for_best_model=args.metric_for_best_model,
        greater_is_better=args.greater_is_better,
        save_total_limit=args.save_total_limit,
        fp16=args.fp16,
        bf16=args.bf16,
        seed=args.train_seed,
        data_seed=args.train_seed,
        report_to=[],
    )


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    atomic_write_json(path, payload)


def write_jsonl(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    env_path = Path(os.getenv("FINETUNE_ENV_FILE", str(DEFAULT_ENV_PATH)))
    load_env_file(env_path)
    parser = build_parser()
    args = parser.parse_args()

    seed_everything(args.train_seed)

    model_name = resolve_model_name(args.model_name)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    log(f"[config] env file: {env_path}")
    log(f"[config] output dir: {output_dir}")
    log(f"[config] model: {model_name}")

    clean_records = discover_skills(args.clean_root, "clean")
    poison_records = discover_skills_from_json(args.poison_json_path, "poisoned_json")

    clean_train, clean_test, clean_split_meta = split_skill_records(
        clean_records,
        test_ratio=args.clean_test_ratio,
        seed=args.split_seed,
    )
    poison_train, poison_test, poison_split_meta = split_skill_records(
        poison_records,
        test_ratio=args.poison_test_ratio,
        seed=args.split_seed,
    )

    train_examples = shuffle_examples(
        build_examples(clean_train, poison_train, "train"),
        seed=args.train_seed,
    )
    test_examples = shuffle_examples(
        build_examples(clean_test, poison_test, "test"),
        seed=args.train_seed,
    )

    log(
        "[data] clean split: "
        f"train={len(clean_train)}, test={len(clean_test)}, seed={args.split_seed}, "
        f"test_ratio={args.clean_test_ratio}"
    )
    log(
        "[data] poison split: "
        f"train={len(poison_train)}, test={len(poison_test)}, seed={args.split_seed}, "
        f"test_ratio={args.poison_test_ratio}"
    )
    log(
        "[data] classification dataset: "
        f"train={len(train_examples)} (clean={len(clean_train)}, poison={len(poison_train)}), "
        f"test={len(test_examples)} (clean={len(clean_test)}, poison={len(poison_test)})"
    )

    split_manifest = {
        "created_at": utc_now_iso(),
        "clean_split": clean_split_meta,
        "poison_split": poison_split_meta,
        "train_examples": [example.to_dict() for example in train_examples],
        "test_examples": [example.to_dict() for example in test_examples],
    }
    write_json(output_dir / "dataset_split.json", split_manifest)

    from datasets import DatasetDict
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        DataCollatorWithPadding,
        Trainer,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def preprocess(batch: Dict[str, List[Any]]) -> Dict[str, Any]:
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=args.max_length,
        )

    raw_datasets = DatasetDict(
        {
            "train": to_hf_dataset(train_examples),
            "test": to_hf_dataset(test_examples),
        }
    )
    tokenized_datasets = raw_datasets.map(
        preprocess,
        batched=True,
        desc="Tokenizing datasets",
    )

    columns_to_keep = {"input_ids", "attention_mask", "label"}
    if "token_type_ids" in tokenized_datasets["train"].column_names:
        columns_to_keep.add("token_type_ids")
    remove_columns = [
        column
        for column in tokenized_datasets["train"].column_names
        if column not in columns_to_keep
    ]
    tokenized_datasets = tokenized_datasets.remove_columns(remove_columns)

    checkpoint_dir = args.checkpoint_dir or output_dir
    if args.eval_only:
        if not checkpoint_dir.exists():
            raise FileNotFoundError(f"checkpoint dir not found: {checkpoint_dir}")
        model_load_path = str(checkpoint_dir)
    else:
        model_load_path = model_name

    model = AutoModelForSequenceClassification.from_pretrained(
        model_load_path,
        num_labels=2,
    )

    training_args = build_training_arguments(args, output_dir)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics_builder(),
    )

    if not args.eval_only:
        log("[train] starting fine-tuning")
        train_result = trainer.train()
        trainer.save_model(str(output_dir / "best_model"))
        tokenizer.save_pretrained(str(output_dir / "best_model"))
        write_json(
            output_dir / "train_metrics.json",
            {
                "created_at": utc_now_iso(),
                "model_name": model_name,
                "train_metrics": train_result.metrics,
            },
        )
        log("[train] fine-tuning completed")
    else:
        log(f"[eval] loading checkpoint from: {checkpoint_dir}")

    metrics = trainer.evaluate(eval_dataset=tokenized_datasets["test"])
    predictions = trainer.predict(tokenized_datasets["test"])

    import numpy as np

    logits = predictions.predictions
    labels = predictions.label_ids
    pred_labels = np.argmax(logits, axis=-1)
    shifted = logits - np.max(logits, axis=-1, keepdims=True)
    probs = np.exp(shifted)
    probs = probs / probs.sum(axis=-1, keepdims=True)

    prediction_rows: List[Dict[str, Any]] = []
    for example, pred_label, prob_row, gold_label in zip(test_examples, pred_labels, probs, labels):
        prediction_rows.append(
            {
                **example.to_dict(),
                "gold_label": int(gold_label),
                "pred_label": int(pred_label),
                "prob_label_0": float(prob_row[0]),
                "prob_label_1": float(prob_row[1]),
                "correct": int(pred_label == gold_label),
            }
        )

    summary = {
        "created_at": utc_now_iso(),
        "model_name": model_name,
        "output_dir": str(output_dir),
        "eval_only": args.eval_only,
        "checkpoint_dir": str(checkpoint_dir) if args.eval_only else str(output_dir / "best_model"),
        "clean_split": clean_split_meta,
        "poison_split": poison_split_meta,
        "train_example_count": len(train_examples),
        "test_example_count": len(test_examples),
        "metrics": metrics,
    }
    write_json(output_dir / "eval_summary.json", summary)
    write_jsonl(output_dir / "test_predictions.jsonl", prediction_rows)

    log(
        "[eval] metrics: "
        f"accuracy={metrics.get('eval_accuracy')}, "
        f"precision={metrics.get('eval_precision')}, "
        f"recall={metrics.get('eval_recall')}, "
        f"f1={metrics.get('eval_f1')}"
    )
    log(f"[done] results written to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
