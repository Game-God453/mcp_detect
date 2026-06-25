#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from train_skill_injection_classifier import (
    ClassificationExample,
    apply_cuda_visible_devices_from_env,
    build_examples,
    compute_metrics_builder,
    load_env_file,
    load_tokenizer,
    paired_category_key,
    paired_group_key,
    resolve_model_name,
    seed_everything,
    shuffle_examples,
    to_hf_dataset,
    write_json,
    write_jsonl,
)
from skill_detection.core import (
    build_detection_text,
    create_timestamped_output_dir,
    discover_paired_skills_from_merged_json,
    split_skill_records_grouped_by_category,
    utc_now_iso,
)


DEFAULT_ENV_PATH = Path(".env")
DEFAULT_MERGED_JSON_PATH = Path("merged_poison_results_20260615.json")
DEFAULT_OUTPUT_DIR = Path("pretrained_eval_runs")


def log(message: str) -> None:
    print(message, flush=True)


def env_str(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def env_int(name: str, default: int | None = None) -> int | None:
    value = env_str(name)
    if value is None:
        return default
    return int(value)


def env_float(name: str, default: float | None = None) -> float | None:
    value = env_str(name)
    if value is None:
        return default
    return float(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate a raw pretrained sequence-classification model on the fixed skill "
            "injection test split without fine-tuning."
        )
    )
    parser.add_argument(
        "--merged-json-path",
        type=Path,
        default=Path(env_str("FINETUNE_MERGED_JSON_PATH", str(DEFAULT_MERGED_JSON_PATH))),
    )
    parser.add_argument(
        "--model-name",
        default=env_str("FINETUNE_MODEL_NAME", "microsoft/deberta-v3-small"),
        help="Pretrained HF model name or path, e.g. microsoft/deberta-v3-small",
    )
    parser.add_argument(
        "--poison-test-json",
        type=Path,
        default=Path(env_str("PRETRAINED_EVAL_POISON_TEST_JSON")) if env_str("PRETRAINED_EVAL_POISON_TEST_JSON") else None,
        help=(
            "Optional regenerated poison test file, e.g. "
            "alt_trigger_eval_runs/.../regenerated_test_poison_rows.json. "
            "When provided, clean test samples still come from the fixed split, "
            "but poison test samples are replaced by this file."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Default: pretrained_eval_runs/<sanitized_model_name>",
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
        "--eval-batch-size",
        type=int,
        default=env_int("FINETUNE_EVAL_BATCH_SIZE", 32),
    )
    return parser


def load_alt_poison_rows(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        rows = payload.get("rows", [])
    else:
        rows = payload
    if not isinstance(rows, list):
        raise ValueError(f"{path} must contain a JSON array or an object with a 'rows' list")
    normalized: List[Dict[str, Any]] = []
    for index, item in enumerate(rows):
        if not isinstance(item, dict):
            raise ValueError(f"{path}[{index}] must be an object")
        source_merged_index = item.get("source_merged_index")
        skill_name = str(item.get("skill_name", "")).strip()
        category = str(item.get("category", "")).strip()
        poisoned_description = str(item.get("poisoned_description", "")).strip()
        trigger = item.get("trigger")
        if source_merged_index is None or not skill_name or not category or not poisoned_description:
            raise ValueError(
                f"{path}[{index}] requires source_merged_index, skill_name, category, and poisoned_description"
            )
        normalized.append(
            {
                "source_merged_index": int(source_merged_index),
                "skill_name": skill_name,
                "category": category,
                "poisoned_description": poisoned_description,
                "trigger": None if trigger is None else str(trigger),
            }
        )
    return normalized


def build_test_examples_with_alt_poison(
    clean_records: List[Any],
    alt_poison_rows: List[Dict[str, Any]],
    split_name: str,
) -> List[ClassificationExample]:
    clean_examples: List[ClassificationExample] = []
    clean_index_to_record: Dict[int, Any] = {}
    for record in clean_records:
        clean_examples.append(
            ClassificationExample(
                example_id=f"{record.record_variant or 'record'}::{record.skill_key}",
                text=record.input_text,
                label=int(record.label),
                source_dataset=record.source_dataset,
                split=split_name,
                skill_name=record.skill_name,
                description=record.description,
                trigger_text=record.trigger_text,
                skill_key=record.skill_key,
            )
        )
        clean_index_to_record[int(record.source_result_index)] = record

    expected_indices = set(clean_index_to_record.keys())
    provided_indices = {int(row["source_merged_index"]) for row in alt_poison_rows}
    if provided_indices != expected_indices:
        missing = sorted(expected_indices - provided_indices)
        extra = sorted(provided_indices - expected_indices)
        raise ValueError(
            "Alternative poison rows do not match the fixed test split. "
            f"missing_indices={missing[:10]} extra_indices={extra[:10]}"
        )

    poison_examples: List[ClassificationExample] = []
    for row in alt_poison_rows:
        merged_index = int(row["source_merged_index"])
        clean_record = clean_index_to_record[merged_index]
        poison_examples.append(
            ClassificationExample(
                example_id=f"alt_poison::{merged_index}::{clean_record.skill_key}",
                text=build_detection_text(row["skill_name"], row["poisoned_description"]),
                label=1,
                source_dataset=str(Path("alt_poison").as_posix()),
                split=split_name,
                skill_name=row["skill_name"],
                description=row["poisoned_description"],
                trigger_text=row.get("trigger"),
                skill_key=f"alt_poison/{merged_index}/poison",
            )
        )

    return clean_examples + poison_examples


def main() -> int:
    env_path = Path(os.getenv("FINETUNE_ENV_FILE", str(DEFAULT_ENV_PATH)))
    load_env_file(env_path)
    apply_cuda_visible_devices_from_env()

    parser = build_parser()
    args = parser.parse_args()

    seed_everything(args.train_seed)

    model_name = resolve_model_name(args.model_name)
    safe_model_name = model_name.replace("/", "__")
    base_output_dir = args.output_dir or (DEFAULT_OUTPUT_DIR / safe_model_name)
    output_dir = create_timestamped_output_dir(base_output_dir)

    log(f"[config] env file: {env_path}")
    log(f"[config] output base dir: {base_output_dir}")
    log(f"[config] output dir: {output_dir}")
    log(f"[config] pretrained model: {model_name}")
    log(
        "[config] poison test source: "
        f"{args.poison_test_json if args.poison_test_json else 'merged_json_default_test_split'}"
    )
    log(f"[config] CUDA_VISIBLE_DEVICES: {os.getenv('CUDA_VISIBLE_DEVICES', '<unset>')}")

    all_records = discover_paired_skills_from_merged_json(
        args.merged_json_path,
        "merged_pairs",
    )
    train_records, test_records, split_meta = split_skill_records_grouped_by_category(
        all_records,
        test_ratio=args.test_ratio,
        seed=args.split_seed,
        group_key_fn=paired_group_key,
        category_key_fn=paired_category_key,
    )

    train_clean_count = sum(1 for record in train_records if record.label == 0)
    train_poison_count = sum(1 for record in train_records if record.label == 1)
    test_clean_count = sum(1 for record in test_records if record.label == 0)
    test_poison_count = sum(1 for record in test_records if record.label == 1)

    train_examples = shuffle_examples(build_examples(train_records, "train"), seed=args.train_seed)
    if args.poison_test_json is None:
        test_examples = shuffle_examples(build_examples(test_records, "test"), seed=args.train_seed)
        test_mode = "merged_default"
    else:
        alt_poison_rows = load_alt_poison_rows(args.poison_test_json)
        clean_test_records = [record for record in test_records if int(record.label) == 0]
        test_examples = shuffle_examples(
            build_test_examples_with_alt_poison(
                clean_records=clean_test_records,
                alt_poison_rows=alt_poison_rows,
                split_name="test",
            ),
            seed=args.train_seed,
        )
        test_mode = "alt_poison_rows"

    log(
        "[data] skill split: "
        f"train_examples={len(train_records)}, test_examples={len(test_records)}, "
        f"pair_groups={split_meta['group_count']}, seed={args.split_seed}, "
        f"test_ratio={args.test_ratio}"
    )
    log(
        "[data] classification dataset: "
        f"train={len(train_examples)} (clean={train_clean_count}, poison={train_poison_count}), "
        f"test={len(test_examples)} (clean={test_clean_count}, poison={test_poison_count}), "
        f"test_mode={test_mode}"
    )

    split_manifest = {
        "created_at": utc_now_iso(),
        "split_metadata": split_meta,
        "test_mode": test_mode,
        "poison_test_json": str(args.poison_test_json) if args.poison_test_json else None,
        "train_examples": [example.to_dict() for example in train_examples],
        "test_examples": [example.to_dict() for example in test_examples],
    }
    write_json(output_dir / "dataset_split.json", split_manifest)

    from datasets import DatasetDict
    from transformers import AutoModelForSequenceClassification, DataCollatorWithPadding, Trainer, TrainingArguments

    tokenizer = load_tokenizer(model_name)

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

    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2,
    )

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        overwrite_output_dir=True,
        do_train=False,
        do_eval=True,
        per_device_eval_batch_size=args.eval_batch_size,
        fp16=False,
        bf16=False,
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        eval_dataset=tokenized_datasets["test"],
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics_builder(),
    )

    log("[eval] evaluating raw pretrained model")
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
        "mode": "pretrained_only",
        "test_mode": test_mode,
        "poison_test_json": str(args.poison_test_json) if args.poison_test_json else None,
        "split_metadata": split_meta,
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
