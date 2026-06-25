#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import random
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import Counter
from multiprocessing import get_context
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from skill_detection.core import (
    atomic_write_json,
    build_detection_text,
    discover_paired_skills_from_merged_json,
    split_skill_records_grouped_by_category,
    utc_now_iso,
)
from train_skill_injection_classifier import apply_cuda_visible_devices_from_env, load_tokenizer


DEFAULT_ENV_PATH = Path(".env")
DEFAULT_MERGED_JSON_PATH = Path("merged_poison_results_20260615.json")
DEFAULT_PROMPTS_JSON_PATH = Path("poison_method/prompt.json")


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


def paired_group_key(record: Any) -> str:
    return str(record.pair_group_id or record.skill_id)


def paired_category_key(record: Any) -> str:
    return str(record.category or record.manifest_category or "unknown")


def load_merged_rows(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("items", [])
    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a JSON array or an items list")
    rows: List[Dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"{path}[{index}] must be an object")
        rows.append(item)
    return rows


def load_json_rows(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        for key in ("rows", "items", "data"):
            if key in payload and isinstance(payload[key], list):
                payload = payload[key]
                break
    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a JSON array or a dict with rows/items/data")
    rows: List[Dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"{path}[{index}] must be an object")
        rows.append(item)
    return rows


def build_eval_examples_from_poison_rows(
    rows: Sequence[Dict[str, Any]],
    source_label: str,
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    eval_examples: List[Dict[str, Any]] = []
    normalized_rows: List[Dict[str, Any]] = []

    for index, item in enumerate(rows):
        skill_name = str(item.get("name") or item.get("skill_name") or "").strip()
        category = str(item.get("category") or "unknown").strip() or "unknown"
        original_description = str(item.get("original_description") or "").strip()
        poisoned_description = str(
            item.get("poisoned_description") or item.get("description") or ""
        ).strip()
        trigger = str(
            item.get("trigger")
            or item.get("gradient_free_suffix")
            or item.get("trigger_text")
            or ""
        ).strip()

        if not skill_name:
            skill_name = f"skill_{index:04d}"
        if not original_description:
            raise ValueError(f"{source_label}[{index}] is missing original_description")
        if not poisoned_description:
            raise ValueError(f"{source_label}[{index}] is missing description/poisoned_description")

        normalized_rows.append(
            {
                "source_index": index,
                "skill_name": skill_name,
                "category": category,
                "original_description": original_description,
                "poisoned_description": poisoned_description,
                "trigger": trigger or None,
            }
        )
        eval_examples.append(
            {
                "example_id": f"{source_label}::ROW{index:04d}::clean",
                "source_row_index": index,
                "record_variant": "clean",
                "skill_name": skill_name,
                "category": category,
                "description": original_description,
                "text": build_detection_text(skill_name, original_description),
                "gold_label": 0,
                "trigger_text": None,
            }
        )
        eval_examples.append(
            {
                "example_id": f"{source_label}::ROW{index:04d}::poison",
                "source_row_index": index,
                "record_variant": "poison",
                "skill_name": skill_name,
                "category": category,
                "description": poisoned_description,
                "text": build_detection_text(skill_name, poisoned_description),
                "gold_label": 1,
                "trigger_text": trigger or None,
            }
        )

    summary = {
        "mode": "poison_test_json",
        "source_label": source_label,
        "row_count": len(normalized_rows),
        "example_count": len(eval_examples),
        "category_counts": dict(Counter(row["category"] for row in normalized_rows)),
    }
    return eval_examples, normalized_rows, summary


def load_prompts(path: Path) -> Dict[str, Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return {str(item["class_name"]): item for item in data}


def get_train_pool_prompts(
    cls: Dict[str, Any],
    train_split_ratio: float,
    rng: Optional[random.Random] = None,
) -> List[str]:
    if "train_prompts" in cls or "test_prompts" in cls:
        return list(cls.get("train_prompts", []))
    prompts = list(cls["prompts"])
    if rng is None:
        random.shuffle(prompts)
    else:
        rng.shuffle(prompts)
    split_idx = math.ceil(len(prompts) * train_split_ratio)
    return prompts[:split_idx]


def build_train_prompt_pools(
    prompt_class_map: Dict[str, Dict[str, Any]],
    train_split_ratio: float,
    seed: int,
) -> Dict[str, List[str]]:
    pools: Dict[str, List[str]] = {}
    for category in sorted(prompt_class_map):
        rng = random.Random(f"{seed}:{category}")
        pools[category] = get_train_pool_prompts(
            prompt_class_map[category],
            train_split_ratio=train_split_ratio,
            rng=rng,
        )
    return pools


def parse_devices(raw_devices: str) -> List[str]:
    devices = [item.strip() for item in raw_devices.split(",") if item.strip()]
    return devices or ["auto"]


def expand_device_slots(devices: List[str], workers_per_device: int) -> List[str]:
    if workers_per_device <= 0:
        raise ValueError("workers_per_device must be positive")
    slots: List[str] = []
    for device in devices:
        for _ in range(workers_per_device):
            slots.append(device)
    return slots


def skill_text(name: str, description: str) -> str:
    return f"name: {name}\ndescription: {description}"


def build_poisoned_description(description: str, trigger: str) -> str:
    trigger = trigger.strip()
    if trigger:
        return f"{description.strip()} {trigger}".strip()
    return description.strip()


def select_topk_train_prompts_for_skill(
    attack: Any,
    skill_name: str,
    description: str,
    train_pool_prompts: Sequence[str],
    topk: int,
) -> List[str]:
    import torch
    import torch.nn.functional as F

    if not train_pool_prompts:
        return []
    if topk <= 0 or topk >= len(train_pool_prompts):
        return list(train_pool_prompts)

    skill_emb = attack.get_embedding(skill_text(skill_name, description))
    pool_emb = attack.get_embedding(list(train_pool_prompts))
    sims = F.cosine_similarity(skill_emb, pool_emb)
    topk_indices = torch.topk(sims, k=topk).indices.tolist()
    return [train_pool_prompts[index] for index in topk_indices]


def poison_skill_once(
    attack: Any,
    skill_name: str,
    description: str,
    train_pool_prompts: Sequence[str],
    topk_train_prompts: int,
) -> str:
    selected_train_prompts = select_topk_train_prompts_for_skill(
        attack=attack,
        skill_name=skill_name,
        description=description,
        train_pool_prompts=train_pool_prompts,
        topk=topk_train_prompts,
    )
    if not selected_train_prompts:
        selected_train_prompts = list(train_pool_prompts)

    trigger, _, _ = attack.run_attack_with_restarts(
        text_pre_trigger=skill_text(skill_name, description),
        text_post_trigger=" ",
        target_texts=selected_train_prompts,
    )
    return trigger


def _regenerate_chunk_worker(
    chunk_tasks: List[Dict[str, Any]],
    worker_config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    import torch

    from poison_method.trigger_attack_skill import AdversarialAttack

    random.seed(worker_config["attack_seed"])
    torch.manual_seed(worker_config["attack_seed"])
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(worker_config["attack_seed"])

    attack_cache: Dict[int, Any] = {}
    results: List[Dict[str, Any]] = []
    for task in chunk_tasks:
        category = task["category"]
        prompt_pool = worker_config["prompt_pools"][category]
        if not prompt_pool:
            raise ValueError(f"category {category!r} has an empty train prompt pool")

        trigger_length = int(task["source_trigger_length"])
        attack = attack_cache.get(trigger_length)
        if attack is None:
            attack = AdversarialAttack(
                emb_model=worker_config["emb_model"],
                trigger_length=trigger_length,
                iterations=worker_config["iterations"],
                top_k=worker_config["top_k"],
                batch_size=worker_config["batch_size"],
                restarts=1,
                words_only=worker_config["words_only"],
                device=worker_config["device"],
            )
            attack_cache[trigger_length] = attack

        trigger = poison_skill_once(
            attack=attack,
            skill_name=task["skill_name"],
            description=task["rewritten_description"],
            train_pool_prompts=prompt_pool,
            topk_train_prompts=worker_config["topk_train_prompts"],
        )
        results.append(
            {
                "source_merged_index": task["source_merged_index"],
                "skill_name": task["skill_name"],
                "category": category,
                "source_trigger_length": trigger_length,
                "alt_emb_model": worker_config["emb_model"],
                "original_description": task["original_description"],
                "rewritten_description": task["rewritten_description"],
                "trigger": trigger,
                "poisoned_description": build_poisoned_description(task["rewritten_description"], trigger),
                "_task_index": task["_task_index"],
                "_device": worker_config["device"],
            }
        )
    return results


def sanitize_name(value: str) -> str:
    return value.replace("/", "__").replace("\\", "__").replace(":", "_")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild the fixed test split with triggers optimized by a different embedding "
            "model on rewritten_description, then evaluate a fine-tuned classifier checkpoint."
        )
    )
    parser.add_argument(
        "--merged-json-path",
        type=Path,
        default=Path(env_str("FINETUNE_MERGED_JSON_PATH", str(DEFAULT_MERGED_JSON_PATH))),
    )
    parser.add_argument(
        "--prompts-json",
        type=Path,
        default=Path(env_str("ALT_TRIGGER_PROMPTS_JSON", str(DEFAULT_PROMPTS_JSON_PATH))),
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=Path(
            env_str(
                "ALT_TRIGGER_CHECKPOINT_DIR",
                env_str("FINETUNE_CHECKPOINT_DIR", "")
                or str(Path(env_str("FINETUNE_OUTPUT_DIR", "finetune_runs/deberta_v3_small")) / "best_model"),
            )
        ),
        help="Fine-tuned classifier checkpoint, typically .../best_model",
    )
    parser.add_argument(
        "--poison-test-json",
        type=Path,
        default=Path(env_str("ALT_TRIGGER_POISON_TEST_JSON")) if env_str("ALT_TRIGGER_POISON_TEST_JSON") else None,
        help=(
            "Optional regenerated poison test file. When omitted, the script evaluates the "
            "fixed merged_poison_results_20260615.json test split."
        ),
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Probability threshold on label=1 for deciding poison vs clean.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Default: alt_trigger_eval_runs/<sanitized_emb_model>",
    )
    parser.add_argument(
        "--split-seed",
        type=int,
        default=env_int("FINETUNE_SPLIT_SEED", 42),
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=env_float("FINETUNE_TEST_RATIO", 0.3),
    )
    parser.add_argument(
        "--attack-seed",
        type=int,
        default=env_int("ALT_TRIGGER_ATTACK_SEED", 42),
    )
    parser.add_argument(
        "--devices",
        type=str,
        default=env_str("ALT_TRIGGER_DEVICES", ""),
        help="Comma-separated devices for parallel trigger regeneration, e.g. cuda:0,cuda:1,cpu.",
    )
    parser.add_argument(
        "--workers-per-device",
        type=int,
        default=env_int("ALT_TRIGGER_WORKERS_PER_DEVICE", 1),
        help="How many worker processes to launch per listed device.",
    )
    parser.add_argument(
        "--emb-model",
        default=env_str("ALT_TRIGGER_EMB_MODEL"),
        help="Alternative embedding model used to optimize triggers. Omit this to only evaluate merged_poison_results_20260615.json.",
    )
    parser.add_argument(
        "--train-split-ratio",
        type=float,
        default=env_float("ALT_TRIGGER_TRAIN_SPLIT_RATIO", 0.8),
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=env_int("ALT_TRIGGER_ITERATIONS", 40),
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=env_int("ALT_TRIGGER_TOP_K", 64),
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=env_int("ALT_TRIGGER_BATCH_SIZE", 256),
    )
    parser.add_argument(
        "--words-only",
        action="store_true",
        default=env_str("ALT_TRIGGER_WORDS_ONLY", "false").lower() in {"1", "true", "yes", "on"},
    )
    parser.add_argument(
        "--topk-train-prompts",
        type=int,
        default=env_int("ALT_TRIGGER_TOPK_TRAIN_PROMPTS", 12),
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=env_int("FINETUNE_MAX_LENGTH", 512),
    )
    parser.add_argument(
        "--eval-batch-size",
        type=int,
        default=env_int("FINETUNE_EVAL_BATCH_SIZE", 32),
    )
    parser.add_argument(
        "--limit-test-pairs",
        type=int,
        default=env_int("ALT_TRIGGER_LIMIT_TEST_PAIRS", None),
        help="Optional debug limit on number of test pairs to regenerate.",
    )
    return parser


def compute_metrics(rows: Sequence[Dict[str, Any]]) -> Dict[str, float]:
    total = len(rows)
    tp = sum(1 for row in rows if row["pred_label"] == 1 and row["gold_label"] == 1)
    tn = sum(1 for row in rows if row["pred_label"] == 0 and row["gold_label"] == 0)
    fp = sum(1 for row in rows if row["pred_label"] == 1 and row["gold_label"] == 0)
    fn = sum(1 for row in rows if row["pred_label"] == 0 and row["gold_label"] == 1)

    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
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
        "example_count": float(total),
    }


def evaluate_with_threshold(
    prediction_rows: Sequence[Dict[str, Any]],
    threshold: float,
) -> List[Dict[str, Any]]:
    adjusted_rows: List[Dict[str, Any]] = []
    for row in prediction_rows:
        prob_1 = float(row["prob_label_1"])
        pred_label = 1 if prob_1 >= threshold else 0
        adjusted_rows.append(
            {
                **row,
                "pred_label": pred_label,
                "correct": int(pred_label == int(row["gold_label"])),
            }
        )
    return adjusted_rows


def write_jsonl(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    env_path = Path(os.getenv("FINETUNE_ENV_FILE", str(DEFAULT_ENV_PATH)))
    load_env_file(env_path)
    apply_cuda_visible_devices_from_env()

    parser = build_parser()
    args = parser.parse_args()

    if not args.checkpoint_dir.exists():
        raise FileNotFoundError(f"checkpoint dir not found: {args.checkpoint_dir}")

    if args.emb_model:
        output_dir = args.output_dir or Path("alt_trigger_eval_runs") / sanitize_name(args.emb_model)
    else:
        output_dir = args.output_dir or Path("finetune_runs") / "recheck_merged_only"
    output_dir.mkdir(parents=True, exist_ok=True)

    random.seed(args.attack_seed)
    os.environ["PYTHONHASHSEED"] = str(args.attack_seed)
    devices = parse_devices(args.devices)
    device_slots = expand_device_slots(devices, args.workers_per_device)

    log(f"[config] env file: {env_path}")
    log(f"[config] merged json: {args.merged_json_path}")
    log(f"[config] prompts json: {args.prompts_json}")
    log(f"[config] checkpoint dir: {args.checkpoint_dir}")
    log(f"[config] output dir: {output_dir}")
    log(f"[config] emb model: {args.emb_model if args.emb_model else '<none>'}")
    log(
        f"[config] devices={devices} workers_per_device={args.workers_per_device} "
        f"total_workers={len(device_slots)}"
    )
    log(f"[config] CUDA_VISIBLE_DEVICES: {os.getenv('CUDA_VISIBLE_DEVICES', '<unset>')}")

    atomic_write_json(
        output_dir / "run_config.json",
        {
            "created_at": utc_now_iso(),
            "merged_json_path": str(args.merged_json_path),
            "prompts_json": str(args.prompts_json),
            "checkpoint_dir": str(args.checkpoint_dir),
            "output_dir": str(output_dir),
            "split_seed": args.split_seed,
            "test_ratio": args.test_ratio,
            "attack_seed": args.attack_seed,
            "devices": devices,
            "workers_per_device": args.workers_per_device,
            "total_workers": len(device_slots),
            "emb_model": args.emb_model,
            "threshold": args.threshold,
            "train_split_ratio": args.train_split_ratio,
            "iterations": args.iterations,
            "top_k": args.top_k,
            "batch_size": args.batch_size,
            "words_only": args.words_only,
            "topk_train_prompts": args.topk_train_prompts,
            "max_length": args.max_length,
            "eval_batch_size": args.eval_batch_size,
            "limit_test_pairs": args.limit_test_pairs,
        },
    )

    merged_rows = load_merged_rows(args.merged_json_path)
    records = discover_paired_skills_from_merged_json(args.merged_json_path, "merged_pairs")
    _, test_records, split_meta = split_skill_records_grouped_by_category(
        records,
        test_ratio=args.test_ratio,
        seed=args.split_seed,
        group_key_fn=paired_group_key,
        category_key_fn=paired_category_key,
    )

    test_row_ids = sorted({int(record.source_result_index) for record in test_records})
    if args.limit_test_pairs is not None:
        test_row_ids = test_row_ids[: args.limit_test_pairs]
    merged_rows_by_index = {int(item.get("merged_index", index)): item for index, item in enumerate(merged_rows)}
    test_rows = [merged_rows_by_index[index] for index in test_row_ids]

    log(
        "[data] fixed test split: "
        f"test_pairs={len(test_rows)}, test_examples={len(test_rows) * 2}, "
        f"seed={args.split_seed}, test_ratio={args.test_ratio}"
    )
    log(f"[data] test categories: {dict(Counter(str(item.get('category', 'unknown')) for item in test_rows))}")

    prompts_by_category = load_prompts(args.prompts_json)
    prompt_pools = build_train_prompt_pools(
        prompt_class_map=prompts_by_category,
        train_split_ratio=args.train_split_ratio,
        seed=args.attack_seed,
    )
    unsupported_categories = sorted(
        {str(item.get('category', '')).strip() for item in test_rows if str(item.get('category', '')).strip() not in prompts_by_category}
    )
    if unsupported_categories:
        raise ValueError(f"No matching prompt class for categories: {unsupported_categories}")

    import numpy as np
    import torch
    from transformers import AutoModelForSequenceClassification

    torch.manual_seed(args.attack_seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.attack_seed)

    eval_examples: List[Dict[str, Any]] = []
    regen_manifest = None
    poison_test_rows: List[Dict[str, Any]] = []
    poison_test_summary: Dict[str, Any] = {}
    if args.poison_test_json is not None:
        poison_test_rows = load_json_rows(args.poison_test_json)
        eval_examples, poison_test_rows, poison_test_summary = build_eval_examples_from_poison_rows(
            poison_test_rows,
            source_label=args.poison_test_json.stem,
        )
        log(
            f"[data] poison test json loaded: rows={len(poison_test_rows)}, "
            f"examples={len(eval_examples)}, source={args.poison_test_json}"
        )
        if args.emb_model:
            log("[data] alt trigger regeneration skipped because poison-test-json was provided")
    elif args.emb_model:
        generated_poison_rows_path = output_dir / "generated_poison_rows.json"
        if generated_poison_rows_path.exists():
            generated_payload = json.loads(generated_poison_rows_path.read_text(encoding="utf-8"))
            if isinstance(generated_payload, dict):
                generated_poison_rows = list(generated_payload.get("rows", []))
            elif isinstance(generated_payload, list):
                generated_poison_rows = generated_payload
            else:
                raise ValueError(f"{generated_poison_rows_path} must contain a JSON object or array")
        else:
            generated_poison_rows = []
        generated_by_index = {
            int(row["source_merged_index"]): row
            for row in generated_poison_rows
            if "source_merged_index" in row
        }

        pending_tasks: List[Dict[str, Any]] = []
        for index, item in enumerate(test_rows, start=1):
            merged_index = int(item.get("merged_index", index - 1))
            if merged_index in generated_by_index:
                log(f"[regen][skip] {index}/{len(test_rows)} merged_index={merged_index}")
                continue

            skill_name = str(item.get("skill_name", "")).strip()
            category = str(item.get("category", "")).strip()
            original_description = str(item.get("original_description", "")).strip()
            rewritten_description = str(item.get("rewritten_description", "")).strip()
            source_trigger_length = int(item.get("trigger_length") or 30)

            if not skill_name or not category or not original_description or not rewritten_description:
                raise ValueError(f"merged row {merged_index} is missing required fields")

            if not prompt_pools.get(category):
                raise ValueError(f"category {category!r} has an empty train prompt pool")

            pending_tasks.append(
                {
                    "_task_index": index - 1,
                    "source_merged_index": merged_index,
                    "skill_name": skill_name,
                    "category": category,
                    "source_trigger_length": source_trigger_length,
                    "original_description": original_description,
                    "rewritten_description": rewritten_description,
                }
            )

        log(
            f"[regen] pending_pairs={len(pending_tasks)} devices={devices} "
            f"workers_per_device={args.workers_per_device} total_workers={len(device_slots)}"
        )

        if pending_tasks:
            if len(device_slots) == 1:
                worker_results = _regenerate_chunk_worker(
                    pending_tasks,
                    {
                        "attack_seed": args.attack_seed,
                        "device": device_slots[0],
                        "prompt_pools": prompt_pools,
                        "emb_model": args.emb_model,
                        "iterations": args.iterations,
                        "top_k": args.top_k,
                        "batch_size": args.batch_size,
                        "words_only": args.words_only,
                        "topk_train_prompts": args.topk_train_prompts,
                    },
                )
                worker_results.sort(key=lambda item: item["_task_index"])
                for completed, row in enumerate(worker_results, start=1):
                    row.pop("_task_index", None)
                    device_used = row.pop("_device", device_slots[0])
                    generated_poison_rows.append(row)
                    generated_by_index[int(row["source_merged_index"])] = row
                    atomic_write_json(
                        generated_poison_rows_path,
                        {
                            "created_at": utc_now_iso(),
                            "emb_model": args.emb_model,
                            "row_count": len(generated_poison_rows),
                            "rows": generated_poison_rows,
                        },
                    )
                    preview = row["trigger"][:120] + ("..." if len(row["trigger"]) > 120 else "")
                    log(
                        f"[regen][{completed}/{len(pending_tasks)}] merged_index={row['source_merged_index']} "
                        f"trigger_length={row['source_trigger_length']} device={device_used} trigger={preview}"
                    )
            else:
                chunks: List[List[Dict[str, Any]]] = [[] for _ in device_slots]
                for index, task in enumerate(pending_tasks):
                    chunks[index % len(device_slots)].append(task)
                worker_jobs = [
                    (device, chunk)
                    for device, chunk in zip(device_slots, chunks)
                    if chunk
                ]
                log(f"[regen] parallel_workers={len(worker_jobs)}")

                with ProcessPoolExecutor(
                    max_workers=len(worker_jobs),
                    mp_context=get_context("spawn"),
                ) as executor:
                    futures = []
                    for worker_index, (device, chunk) in enumerate(worker_jobs):
                        worker_config = {
                            "attack_seed": args.attack_seed + worker_index,
                            "device": device,
                            "prompt_pools": prompt_pools,
                            "emb_model": args.emb_model,
                            "iterations": args.iterations,
                            "top_k": args.top_k,
                            "batch_size": args.batch_size,
                            "words_only": args.words_only,
                            "topk_train_prompts": args.topk_train_prompts,
                        }
                        futures.append(executor.submit(_regenerate_chunk_worker, chunk, worker_config))

                    completed = 0
                    for future in as_completed(futures):
                        worker_results = future.result()
                        worker_results.sort(key=lambda item: item["_task_index"])
                        for row in worker_results:
                            row.pop("_task_index", None)
                            device_used = row.pop("_device", "unknown")
                            generated_poison_rows.append(row)
                            generated_by_index[int(row["source_merged_index"])] = row
                            atomic_write_json(
                                generated_poison_rows_path,
                                {
                                    "created_at": utc_now_iso(),
                                    "emb_model": args.emb_model,
                                    "row_count": len(generated_poison_rows),
                                    "rows": generated_poison_rows,
                                },
                            )
                            completed += 1
                            preview = row["trigger"][:120] + ("..." if len(row["trigger"]) > 120 else "")
                            log(
                                f"[regen][{completed}/{len(pending_tasks)}] merged_index={row['source_merged_index']} "
                                f"trigger_length={row['source_trigger_length']} device={device_used} trigger={preview}"
                            )

        ordered_poison_rows = [generated_by_index[int(item.get("merged_index"))] for item in test_rows]
        atomic_write_json(
            output_dir / "regenerated_test_poison_rows.json",
            {
                "created_at": utc_now_iso(),
                "emb_model": args.emb_model,
                "row_count": len(ordered_poison_rows),
                "rows": ordered_poison_rows,
            },
        )
        regen_manifest = ordered_poison_rows
        for item in test_rows:
            merged_index = int(item["merged_index"])
            skill_name = str(item["skill_name"]).strip()
            category = str(item["category"]).strip()
            original_description = str(item["original_description"]).strip()
            regen = generated_by_index[merged_index]

            eval_examples.append(
                {
                    "example_id": f"alt_trigger::MERGED{merged_index:04d}::clean",
                    "source_merged_index": merged_index,
                    "record_variant": "clean",
                    "skill_name": skill_name,
                    "category": category,
                    "description": original_description,
                    "text": build_detection_text(skill_name, original_description),
                    "gold_label": 0,
                    "trigger_text": None,
                }
            )
            eval_examples.append(
                {
                    "example_id": f"alt_trigger::MERGED{merged_index:04d}::poison",
                    "source_merged_index": merged_index,
                    "record_variant": "poison",
                    "skill_name": skill_name,
                    "category": category,
                    "description": regen["poisoned_description"],
                    "text": build_detection_text(skill_name, regen["poisoned_description"]),
                    "gold_label": 1,
                    "trigger_text": regen["trigger"],
                }
            )
    else:
        for item in test_rows:
            merged_index = int(item["merged_index"])
            skill_name = str(item["skill_name"]).strip()
            category = str(item["category"]).strip()
            original_description = str(item["original_description"]).strip()
            poisoned_description = str(item["poisoned_description"]).strip()
            trigger = str(item.get("trigger", "") or "")

            eval_examples.append(
                {
                    "example_id": f"merged::MERGED{merged_index:04d}::clean",
                    "source_merged_index": merged_index,
                    "record_variant": "clean",
                    "skill_name": skill_name,
                    "category": category,
                    "description": original_description,
                    "text": build_detection_text(skill_name, original_description),
                    "gold_label": 0,
                    "trigger_text": None,
                }
            )
            eval_examples.append(
                {
                    "example_id": f"merged::MERGED{merged_index:04d}::poison",
                    "source_merged_index": merged_index,
                    "record_variant": "poison",
                    "skill_name": skill_name,
                    "category": category,
                    "description": poisoned_description,
                    "text": build_detection_text(skill_name, poisoned_description),
                    "gold_label": 1,
                    "trigger_text": trigger,
                }
            )

    tokenizer = load_tokenizer(str(args.checkpoint_dir))
    model = AutoModelForSequenceClassification.from_pretrained(str(args.checkpoint_dir), num_labels=2)
    model.eval()

    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    model.to(device)
    log(f"[eval] classifier device: {device}")

    prediction_rows: List[Dict[str, Any]] = []
    batch_size = args.eval_batch_size
    for start in range(0, len(eval_examples), batch_size):
        batch = eval_examples[start : start + batch_size]
        encoded = tokenizer(
            [example["text"] for example in batch],
            truncation=True,
            max_length=args.max_length,
            padding=True,
            return_tensors="pt",
        )
        encoded = {key: value.to(device) for key, value in encoded.items()}

        with torch.no_grad():
            outputs = model(**encoded)
            logits = outputs.logits.detach().cpu().numpy()

        shifted = logits - np.max(logits, axis=-1, keepdims=True)
        probs = np.exp(shifted)
        probs = probs / probs.sum(axis=-1, keepdims=True)
        for example, prob_row in zip(batch, probs):
            pred_label = 1 if float(prob_row[1]) >= args.threshold else 0
            prediction_rows.append(
                {
                    **example,
                    "pred_label": int(pred_label),
                    "prob_label_0": float(prob_row[0]),
                    "prob_label_1": float(prob_row[1]),
                    "correct": int(int(pred_label) == int(example["gold_label"])),
                }
            )

    metrics = compute_metrics(prediction_rows)
    summary_test_pairs = len(poison_test_rows) if poison_test_rows else len(test_rows)
    summary_category_counts = (
        dict(Counter(row["category"] for row in poison_test_rows))
        if poison_test_rows
        else dict(Counter(str(item.get("category", "unknown")) for item in test_rows))
    )
    summary_trigger_counts = (
        {}
        if poison_test_rows
        else dict(Counter(int(item.get("trigger_length") or 30) for item in test_rows))
    )

    summary = {
        "created_at": utc_now_iso(),
        "merged_json_path": str(args.merged_json_path),
        "prompts_json": str(args.prompts_json),
        "checkpoint_dir": str(args.checkpoint_dir),
        "output_dir": str(output_dir),
        "emb_model": args.emb_model,
        "threshold": args.threshold,
        "split_seed": args.split_seed,
        "test_ratio": args.test_ratio,
        "attack_seed": args.attack_seed,
        "test_mode": "poison_test_json" if args.poison_test_json else ("alt_poison_rows" if args.emb_model else "merged_only"),
        "poison_test_json": str(args.poison_test_json) if args.poison_test_json else None,
        "poison_test_summary": poison_test_summary or None,
        "test_pair_count": summary_test_pairs,
        "test_example_count": len(eval_examples),
        "trigger_length_counts": summary_trigger_counts,
        "category_counts": summary_category_counts,
        "metrics": metrics,
        "split_metadata": split_meta,
    }

    atomic_write_json(output_dir / "eval_summary.json", summary)
    write_jsonl(output_dir / "test_predictions.jsonl", prediction_rows)

    log(
        "[done] metrics: "
        f"accuracy={metrics['accuracy']:.4f}, "
        f"precision={metrics['precision']:.4f}, "
        f"recall={metrics['recall']:.4f}, "
        f"f1={metrics['f1']:.4f}"
    )
    log(f"[done] results written to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
