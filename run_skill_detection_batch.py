#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, ThreadPoolExecutor, wait
from multiprocessing import get_context
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from skill_detection.core import (
    DEFAULT_PPL_MODEL_NAME,
    KnownAnswerLLMDetector,
    PerplexityDetectors,
    append_jsonl,
    atomic_write_json,
    build_summary,
    create_timestamped_output_dir,
    discover_paired_skills_from_detection_json,
    init_ppl_worker,
    latest_rows_by_skill,
    load_jsonl,
    resolve_known_answer_config,
    resolve_rebuff_config,
    run_ppl_chunk,
    split_skill_records_grouped_by_category,
    utc_now_iso,
)


DEFAULT_OUTPUT_DIR = Path("detection_runs/poisoned_skill_sample100")
DEFAULT_ENV_PATH = Path(".env")
DEFAULT_MERGED_JSON_DATASET_PATH = Path("merged_poison_results_20260615.json")
DEFAULT_DATASET_JSON_PATH = DEFAULT_MERGED_JSON_DATASET_PATH
DEFAULT_MAINSTREAM_PPL_MODELS = ("gpt2", "bert-base-uncased", "xlnet-base-cased")

ALL_METHODS = ("rebuff_llm", "known_answer_detection", "ppl", "ppl_windowed")


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


def env_csv(name: str, default: Optional[Iterable[str]] = None) -> List[str]:
    value = env_str(name)
    if value is None:
        return list(default or [])
    return [item.strip() for item in value.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Batch-detect poisoned skills using rebuff_llm, known_answer_detection, "
            "ppl, and ppl_windowed. The detection input is restricted to skill "
            "name + description."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(env_str("SKILL_DETECT_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR))),
    )
    parser.add_argument(
        "--dataset-json-path",
        type=Path,
        default=Path(
            env_str(
                "SKILL_DETECT_DATASET_JSON_PATH",
                env_str("SKILL_DETECT_MERGED_JSON_PATH", str(DEFAULT_DATASET_JSON_PATH)),
            )
        ),
        help=(
            "Paired JSON dataset used for batch detection and train/test splitting. "
            "Supports both merged_poison_results_20260615.json and flat paired poison files "
            "such as gradient_free_poisoned_skills.json."
        ),
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=env_float("SKILL_DETECT_TEST_RATIO", 0.3),
        help="Per-category test split ratio for skill-level paired splitting.",
    )
    parser.add_argument(
        "--split-seed",
        type=int,
        default=env_int("SKILL_DETECT_SPLIT_SEED", 42),
        help="Random seed used for skill-level paired splitting.",
    )
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=ALL_METHODS,
        default=env_csv("SKILL_DETECT_METHODS", ALL_METHODS),
        help="Subset of detection methods to run.",
    )
    parser.add_argument("--limit", type=int, default=env_int("SKILL_DETECT_LIMIT", None))
    parser.add_argument("--retry-errors", action="store_true", default=env_bool("SKILL_DETECT_RETRY_ERRORS", False))
    parser.add_argument("--stop-on-error", action="store_true", default=env_bool("SKILL_DETECT_STOP_ON_ERROR", False))

    parser.add_argument(
        "--ppl-model",
        default=env_str("PPL_MODEL", DEFAULT_PPL_MODEL_NAME),
        help="Hugging Face causal LM used for PPL/PPL-W scoring. Default follows the GPT-2 family.",
    )
    parser.add_argument(
        "--ppl-models",
        default=env_str("PPL_MODELS", ""),
        help=(
            "Comma-separated PPL backbones to evaluate in one run. "
            f"Recommended mainstream trio: {','.join(DEFAULT_MAINSTREAM_PPL_MODELS)}. "
            "If empty, falls back to --ppl-model."
        ),
    )
    parser.add_argument(
        "--ppl-device",
        default=env_str("PPL_DEVICE", "auto"),
        help="Device for the PPL model, e.g. auto/cpu/cuda/cuda:0.",
    )
    parser.add_argument(
        "--ppl-devices",
        default=env_str("PPL_DEVICES", ""),
        help="Comma-separated devices for parallel PPL inference, e.g. cuda:0,cuda:1,cuda:2.",
    )
    parser.add_argument(
        "--ppl-cache-dir",
        type=Path,
        default=Path(env_str("PPL_CACHE_DIR")) if env_str("PPL_CACHE_DIR") else None,
        help="Optional Hugging Face cache directory for the PPL model.",
    )
    parser.add_argument(
        "--ppl-dtype",
        default=env_str("PPL_DTYPE", "auto"),
        help="PPL model dtype: auto, float16/fp16, bfloat16/bf16, float32/fp32.",
    )
    parser.add_argument(
        "--ppl-batch-size",
        type=int,
        default=env_int("PPL_BATCH_SIZE", 32),
        help="Batch size for PPL forward passes.",
    )
    parser.add_argument(
        "--ppl-chunk-size",
        type=int,
        default=env_int("PPL_CHUNK_SIZE", 8),
        help="How many skills a single PPL worker job processes.",
    )
    parser.add_argument("--calibration-sample-size", type=int, default=env_int("PPL_CALIBRATION_SAMPLE_SIZE", 100))
    parser.add_argument("--calibration-seed", type=int, default=env_int("PPL_CALIBRATION_SEED", 42))
    parser.add_argument("--target-fpr", type=float, default=env_float("PPL_TARGET_FPR", 0.01))
    parser.add_argument(
        "--window-size",
        type=str,
        default=env_str("PPL_WINDOW_SIZE", "auto"),
        help="Use an integer or 'auto'. Auto picks 5/10 from clean token lengths.",
    )

    parser.add_argument("--rebuff-api-key", default=env_str("REBUFF_OPENAI_API_KEY"))
    parser.add_argument("--rebuff-api-base", default=env_str("REBUFF_OPENAI_API_BASE"))
    parser.add_argument("--rebuff-model", default=env_str("REBUFF_OPENAI_MODEL"))
    parser.add_argument(
        "--rebuff-thinking-type",
        default=env_str("REBUFF_OPENAI_THINKING"),
        help="Optional DeepSeek thinking mode, e.g. disabled/enabled.",
    )
    parser.add_argument("--rebuff-threshold", type=float, default=env_float("REBUFF_THRESHOLD", 0.9))
    parser.add_argument(
        "--known-answer-secret",
        default=env_str("KNOWN_ANSWER_SECRET", "Hello World!"),
        help="Secret text used by paper-style known-answer detection.",
    )
    parser.add_argument(
        "--rebuff-max-workers",
        type=int,
        default=env_int("REBUFF_MAX_WORKERS", 16),
        help="Max concurrent LLM API calls for rebuff_llm and known_answer_detection.",
    )
    return parser


def parse_window_size(raw_value: str) -> int | None:
    if raw_value == "auto":
        return None
    value = int(raw_value)
    if value <= 0:
        raise ValueError("window size must be a positive integer")
    return value


def method_error_payload(error: Exception) -> Dict[str, Any]:
    return {"status": "error", "error_type": type(error).__name__, "error": str(error)}


def parse_device_list(raw_devices: str, fallback_device: str) -> List[str]:
    devices = [item.strip() for item in raw_devices.split(",") if item.strip()]
    return devices or [fallback_device]


def parse_model_list(raw_models: str, fallback_model: str) -> List[str]:
    models = [item.strip() for item in raw_models.split(",") if item.strip()]
    return models or [fallback_model]


def infer_ppl_scoring_mode(model_name: str) -> str:
    lowered = model_name.lower()
    if "bert" in lowered and "xlnet" not in lowered:
        return "masked"
    return "causal"


def build_ppl_method_name(base_method: str, model_name: str, multi_model: bool) -> str:
    if not multi_model:
        return base_method
    return f"{base_method}@{model_name}"


def chunk_list(values: List[Dict[str, Any]], chunk_size: int) -> List[List[Dict[str, Any]]]:
    if chunk_size <= 0:
        raise ValueError("chunk size must be positive")
    return [values[index : index + chunk_size] for index in range(0, len(values), chunk_size)]


def paired_group_key(record: Any) -> str:
    return str(record.pair_group_id or record.skill_id)


def paired_category_key(record: Any) -> str:
    return str(record.category or record.manifest_category or "unknown")


def llm_task(method_name: str, skill_key: str, text: str, detector: Any) -> Dict[str, Any]:
    return {"skill_key": skill_key, "methods": {method_name: {"status": "ok", **detector.detect(text)}}}


def row_is_retryable(previous: Optional[Dict[str, Any]], method: str, retry_errors: bool) -> bool:
    if previous is None:
        return True
    status = previous.get("methods", {}).get(method, {}).get("status")
    if status == "ok" or status == "skipped":
        return False
    if status == "error":
        return retry_errors
    return True


def merge_skill_result(
    skill_key: str,
    method_updates: Dict[str, Dict[str, Any]],
    records_by_skill: Dict[str, Any],
    latest_rows: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    record = records_by_skill[skill_key]
    previous = latest_rows.get(skill_key, {})
    merged_methods = dict(previous.get("methods", {}))
    merged_methods.update(method_updates)
    errors = []
    for method_name, payload in merged_methods.items():
        if payload.get("status") == "error":
            errors.append(f"{method_name}: {payload.get('error')}")
    row = {
        **record.to_dict(),
        "processed_at": utc_now_iso(),
        "methods": merged_methods,
        "had_errors": bool(errors),
        "errors": errors,
    }
    latest_rows[skill_key] = row
    return row


def main() -> int:
    env_path = Path(os.getenv("SKILL_DETECT_ENV_FILE", str(DEFAULT_ENV_PATH)))
    load_env_file(env_path)

    parser = build_parser()
    args = parser.parse_args()

    base_output_dir: Path = args.output_dir
    output_dir = create_timestamped_output_dir(base_output_dir)
    results_path = output_dir / "results.jsonl"
    state_path = output_dir / "run_state.json"
    summary_path = output_dir / "summary.json"

    ppl_model_names = parse_model_list(args.ppl_models, args.ppl_model)
    use_ppl_methods = "ppl" in args.methods or "ppl_windowed" in args.methods
    ppl_multi_model = use_ppl_methods and len(ppl_model_names) > 1
    ppl_method_specs: List[Dict[str, Any]] = []
    actual_methods = list(args.methods)
    if use_ppl_methods:
        actual_methods = [
            method_name
            for method_name in actual_methods
            if method_name not in {"ppl", "ppl_windowed"}
        ]
        for model_name in ppl_model_names:
            if "ppl" in args.methods:
                actual_methods.append(
                    build_ppl_method_name("ppl", model_name, ppl_multi_model)
                )
            if "ppl_windowed" in args.methods:
                actual_methods.append(
                    build_ppl_method_name("ppl_windowed", model_name, ppl_multi_model)
                )

    log(f"[config] env file: {env_path}")
    log(f"[config] output base dir: {base_output_dir}")
    log(f"[config] output dir: {output_dir}")
    log(f"[config] dataset json: {args.dataset_json_path}")
    log(f"[config] methods: {', '.join(args.methods)}")
    if use_ppl_methods:
        log(f"[config] ppl backbones: {', '.join(ppl_model_names)}")

    split_metadata: Optional[Dict[str, Any]] = None
    train_records: List[Any] = []

    dataset_records = discover_paired_skills_from_detection_json(
        json_path=args.dataset_json_path,
        source_dataset="detection_pairs",
    )
    train_records, test_records, split_metadata = split_skill_records_grouped_by_category(
        dataset_records,
        test_ratio=args.test_ratio,
        seed=args.split_seed,
        group_key_fn=paired_group_key,
        category_key_fn=paired_category_key,
    )
    clean_records = [record for record in train_records if record.label == 0]
    log(
        "[data] paired dataset loaded: "
        f"total_examples={len(dataset_records)}, train={len(train_records)}, test={len(test_records)}, "
        f"seed={args.split_seed}, test_ratio={args.test_ratio}, "
        f"pair_groups={split_metadata['group_count']}"
    )

    if args.limit is not None:
        test_records = test_records[: args.limit]

    log(f"[data] clean skills for thresholding: {len(clean_records)}")
    log(f"[data] test records: {len(test_records)}")

    existing_rows = load_jsonl(results_path)
    latest_rows = latest_rows_by_skill(existing_rows)
    records_by_skill = {record.skill_key: record for record in test_records}

    thresholds: Dict[str, Any] = {}
    if use_ppl_methods:
        ppl_devices = parse_device_list(args.ppl_devices, args.ppl_device)
        thresholds["perplexity"] = {}
        log(
            "[ppl] calibrating thresholds with "
            f"models={','.join(ppl_model_names)}, devices={','.join(ppl_devices)}, "
            f"batch_size={args.ppl_batch_size}, window_size={args.window_size}"
        )
        for model_name in ppl_model_names:
            scoring_mode = infer_ppl_scoring_mode(model_name)
            ppl_method_name = build_ppl_method_name("ppl", model_name, ppl_multi_model)
            ppl_windowed_method_name = build_ppl_method_name(
                "ppl_windowed",
                model_name,
                ppl_multi_model,
            )
            ppl_detectors = PerplexityDetectors(
                model_name_or_path=model_name,
                device=ppl_devices[0],
                cache_dir=args.ppl_cache_dir,
                dtype=args.ppl_dtype,
                scoring_mode=scoring_mode,
                inference_batch_size=args.ppl_batch_size,
                calibration_sample_size=args.calibration_sample_size,
                calibration_seed=args.calibration_seed,
                target_fpr=args.target_fpr,
                window_size=parse_window_size(args.window_size),
            )
            fit_payload = ppl_detectors.fit(clean_records)
            ppl_detectors.release()
            thresholds["perplexity"][model_name] = {
                **fit_payload,
                "scoring_mode": scoring_mode,
                "ppl_method_name": ppl_method_name,
                "ppl_windowed_method_name": ppl_windowed_method_name,
            }
            ppl_method_specs.append(
                {
                    "model_name": model_name,
                    "scoring_mode": scoring_mode,
                    "ppl_method_name": ppl_method_name,
                    "ppl_windowed_method_name": ppl_windowed_method_name,
                    "thresholds": thresholds["perplexity"][model_name],
                }
            )
            log(
                "[ppl] calibrated: "
                f"model={model_name}, scoring_mode={scoring_mode}, "
                f"log_threshold={fit_payload['ppl_log_threshold']:.4f}, "
                f"window_log_threshold={fit_payload['ppl_window_log_threshold']:.4f}, "
                f"window_size={fit_payload['window_size']}"
            )

    rebuff_detector = None
    known_answer_detector = None
    if "rebuff_llm" in args.methods:
        rebuff_detector = resolve_rebuff_config(
            cli_api_key=args.rebuff_api_key,
            cli_model=args.rebuff_model,
            cli_api_base=args.rebuff_api_base,
            cli_threshold=args.rebuff_threshold,
            cli_thinking_type=args.rebuff_thinking_type,
        )
        thresholds["rebuff_llm"] = {
            "threshold": args.rebuff_threshold,
            "api_base": rebuff_detector.api_base,
            "model": rebuff_detector.model,
        }
        log(
            "[rebuff] configured: "
            f"model={rebuff_detector.model}, base={rebuff_detector.api_base}, "
            f"max_workers={args.rebuff_max_workers}"
        )
    if "known_answer_detection" in args.methods:
        known_answer_detector = resolve_known_answer_config(
            cli_api_key=args.rebuff_api_key,
            cli_model=args.rebuff_model,
            cli_api_base=args.rebuff_api_base,
            cli_secret_text=args.known_answer_secret,
            cli_thinking_type=args.rebuff_thinking_type,
        )
        thresholds["known_answer_detection"] = {
            "api_base": known_answer_detector.api_base,
            "model": known_answer_detector.model,
            "secret_text": known_answer_detector.secret_text,
        }
        log(
            "[known-answer] configured: "
            f"model={known_answer_detector.model}, base={known_answer_detector.api_base}, "
            f"secret={known_answer_detector.secret_text!r}, max_workers={args.rebuff_max_workers}"
        )

    config_payload = {
        "started_at": utc_now_iso(),
        "dataset_json_path": str(args.dataset_json_path),
        "merged_json_path": str(args.dataset_json_path),
        "test_ratio": args.test_ratio,
        "split_seed": args.split_seed,
        "output_dir": str(output_dir),
        "methods": args.methods,
        "actual_methods": actual_methods,
        "limit": args.limit,
        "retry_errors": args.retry_errors,
        "env_file": str(env_path),
        "thresholds": thresholds,
        "split_metadata": split_metadata,
    }

    if split_metadata is not None:
        split_manifest_path = output_dir / "dataset_split.json"
        atomic_write_json(
            split_manifest_path,
            {
                "source_path": str(args.dataset_json_path),
                "seed": args.split_seed,
                "test_ratio": args.test_ratio,
                "split_metadata": split_metadata,
                "train_records": [record.to_dict() for record in train_records],
                "test_records": [record.to_dict() for record in test_records],
            },
        )
        log(f"[data] split manifest written to: {split_manifest_path}")

    def persist_state() -> None:
        total_examples = len(test_records)
        total_skill_pairs = len({paired_group_key(record) for record in test_records})
        summary = build_summary(
            rows=list(latest_rows.values()),
            requested_methods=actual_methods,
            total_examples=total_examples,
            total_skill_pairs=total_skill_pairs,
        )
        atomic_write_json(
            state_path,
            {
                **config_payload,
                "last_updated_at": utc_now_iso(),
                "progress": {
                    "total_examples": total_examples,
                    "completed_examples": len(latest_rows),
                    "remaining_examples": max(0, total_examples - len(latest_rows)),
                    "total_skill_pairs": total_skill_pairs,
                    "completed_skill_pairs": len(
                        {row.get("pair_group_id") for row in latest_rows.values() if row.get("pair_group_id")}
                    ),
                    "remaining_skill_pairs": max(
                        0,
                        total_skill_pairs
                        - len(
                            {
                                row.get("pair_group_id")
                                for row in latest_rows.values()
                                if row.get("pair_group_id")
                            }
                        ),
                    ),
                },
                "summary": summary,
            },
        )
        atomic_write_json(summary_path, summary)

    persist_state()

    llm_jobs: List[Dict[str, Any]] = []
    ppl_jobs_by_model: List[Dict[str, Any]] = []

    for record in test_records:
        previous = latest_rows.get(record.skill_key)
        need_rebuff = "rebuff_llm" in args.methods and row_is_retryable(
            previous, "rebuff_llm", args.retry_errors
        )
        need_known_answer = "known_answer_detection" in args.methods and row_is_retryable(
            previous, "known_answer_detection", args.retry_errors
        )
        need_ppl = "ppl" in args.methods and row_is_retryable(
            previous, "ppl", args.retry_errors
        )
        need_ppl_windowed = "ppl_windowed" in args.methods and row_is_retryable(
            previous, "ppl_windowed", args.retry_errors
        )

        if need_rebuff:
            llm_jobs.append(
                {
                    "method_name": "rebuff_llm",
                    "record": record,
                    "detector": rebuff_detector,
                }
            )
        if need_known_answer:
            llm_jobs.append(
                {
                    "method_name": "known_answer_detection",
                    "record": record,
                    "detector": known_answer_detector,
                }
            )
        for spec in ppl_method_specs:
            need_model_ppl = "ppl" in args.methods and row_is_retryable(
                previous,
                spec["ppl_method_name"],
                args.retry_errors,
            )
            need_model_ppl_windowed = "ppl_windowed" in args.methods and row_is_retryable(
                previous,
                spec["ppl_windowed_method_name"],
                args.retry_errors,
            )
            if not need_model_ppl and not need_model_ppl_windowed:
                continue
            model_job_bucket = next(
                (
                    bucket
                    for bucket in ppl_jobs_by_model
                    if bucket["model_name"] == spec["model_name"]
                ),
                None,
            )
            if model_job_bucket is None:
                model_job_bucket = {**spec, "jobs": []}
                ppl_jobs_by_model.append(model_job_bucket)
            model_job_bucket["jobs"].append(
                {
                    "skill_key": record.skill_key,
                    "input_text": record.input_text,
                    "need_ppl": need_model_ppl,
                    "need_ppl_windowed": need_model_ppl_windowed,
                }
            )

    log(
        "[plan] pending jobs: "
        f"llm={len(llm_jobs)}, "
        f"ppl_like={sum(len(bucket['jobs']) for bucket in ppl_jobs_by_model)}"
    )

    future_map: Dict[Any, Tuple[str, Any]] = {}
    rebuff_executor: Optional[ThreadPoolExecutor] = None
    completed_llm = 0
    completed_ppl_like = 0
    llm_error_count = 0
    ppl_error_count = 0

    try:
        if llm_jobs:
            rebuff_executor = ThreadPoolExecutor(max_workers=max(1, args.rebuff_max_workers))
            for job in llm_jobs:
                record = job["record"]
                method_name = job["method_name"]
                detector = job["detector"]
                assert detector is not None
                future = rebuff_executor.submit(
                    llm_task,
                    method_name,
                    record.skill_key,
                    record.input_text,
                    detector,
                )
                future_map[future] = ("llm", (method_name, record.skill_key))
            log(f"[llm] submitted {len(llm_jobs)} requests")

        if not future_map and not any(bucket["jobs"] for bucket in ppl_jobs_by_model):
            log("[done] no pending work; all requested methods already completed")

        while future_map:
            done, _ = wait(set(future_map.keys()), return_when=FIRST_COMPLETED)
            for future in done:
                future_type, future_context = future_map.pop(future)
                try:
                    result = future.result()
                except Exception as error:
                    if args.stop_on_error:
                        raise
                    if future_type == "llm":
                        method_name, skill_key = future_context
                        llm_error_count += 1
                        row = merge_skill_result(
                            skill_key=skill_key,
                            method_updates={method_name: method_error_payload(error)},
                            records_by_skill=records_by_skill,
                            latest_rows=latest_rows,
                        )
                        append_jsonl(results_path, row)
                        persist_state()
                        log(
                            f"[{method_name}][error] {skill_key}: {type(error).__name__}: {error}"
                        )
                    else:
                        ppl_error_count += len(future_context)
                        for skill_key in future_context:
                            row = merge_skill_result(
                                skill_key=skill_key,
                                method_updates={
                                    method_name: method_error_payload(error)
                                    for method_name in ("ppl", "ppl_windowed")
                                    if method_name in args.methods
                                },
                                records_by_skill=records_by_skill,
                                latest_rows=latest_rows,
                            )
                            append_jsonl(results_path, row)
                            persist_state()
                        log(
                            "[ppl][error] chunk failed for "
                            f"{len(future_context)} skills: {type(error).__name__}: {error}"
                        )
                    continue

                if future_type == "llm":
                    skill_key = result["skill_key"]
                    method_name = next(iter(result["methods"].keys()))
                    row = merge_skill_result(
                        skill_key=skill_key,
                        method_updates=result["methods"],
                        records_by_skill=records_by_skill,
                        latest_rows=latest_rows,
                    )
                    append_jsonl(results_path, row)
                    persist_state()
                    completed_llm += 1
                    llm_status = row["methods"][method_name]["status"]
                    llm_flagged = row["methods"][method_name].get("flagged")
                    log(
                        f"[{method_name}][{completed_llm}/{len(llm_jobs)}] "
                        f"{skill_key} status={llm_status} flagged={llm_flagged}"
                    )
    finally:
        if rebuff_executor is not None:
            rebuff_executor.shutdown(wait=True, cancel_futures=False)

    for model_bucket in ppl_jobs_by_model:
        model_name = model_bucket["model_name"]
        scoring_mode = model_bucket["scoring_mode"]
        model_jobs = model_bucket["jobs"]
        if not model_jobs:
            continue

        ppl_devices = parse_device_list(args.ppl_devices, args.ppl_device)
        mp_context = get_context("spawn")
        ppl_executors: List[ProcessPoolExecutor] = []
        ppl_future_map: Dict[Any, Dict[str, Any]] = {}
        ppl_chunks = chunk_list(model_jobs, args.ppl_chunk_size)
        total_model_jobs = len(model_jobs)

        try:
            for device in ppl_devices:
                executor = ProcessPoolExecutor(
                    max_workers=1,
                    mp_context=mp_context,
                    initializer=init_ppl_worker,
                    initargs=(
                        model_name,
                        device,
                        str(args.ppl_cache_dir) if args.ppl_cache_dir else None,
                        args.ppl_dtype,
                        scoring_mode,
                        args.ppl_batch_size,
                    ),
                )
                ppl_executors.append(executor)

            log(
                "[ppl] submitted "
                f"model={model_name}, chunks={len(ppl_chunks)}, workers={len(ppl_executors)}"
            )
            for index, chunk in enumerate(ppl_chunks):
                executor = ppl_executors[index % len(ppl_executors)]
                future = executor.submit(
                    run_ppl_chunk,
                    chunk,
                    model_bucket["ppl_method_name"],
                    model_bucket["ppl_windowed_method_name"],
                    model_bucket["thresholds"].get("ppl_log_threshold"),
                    model_bucket["thresholds"].get("ppl_window_log_threshold"),
                    int(model_bucket["thresholds"]["window_size"]),
                )
                ppl_future_map[future] = {
                    "skill_keys": [item["skill_key"] for item in chunk],
                    "method_names": [
                        method_name
                        for method_name in (
                            model_bucket["ppl_method_name"],
                            model_bucket["ppl_windowed_method_name"],
                        )
                        if method_name in actual_methods
                    ],
                    "model_name": model_name,
                }

            while ppl_future_map:
                done, _ = wait(set(ppl_future_map.keys()), return_when=FIRST_COMPLETED)
                for future in done:
                    future_context = ppl_future_map.pop(future)
                    try:
                        result = future.result()
                    except Exception as error:
                        if args.stop_on_error:
                            raise
                        ppl_error_count += len(future_context["skill_keys"])
                        for skill_key in future_context["skill_keys"]:
                            row = merge_skill_result(
                                skill_key=skill_key,
                                method_updates={
                                    method_name: method_error_payload(error)
                                    for method_name in future_context["method_names"]
                                },
                                records_by_skill=records_by_skill,
                                latest_rows=latest_rows,
                            )
                            append_jsonl(results_path, row)
                            persist_state()
                        log(
                            "[ppl][error] "
                            f"model={future_context['model_name']} chunk failed for "
                            f"{len(future_context['skill_keys'])} skills: {type(error).__name__}: {error}"
                        )
                        continue

                    completed_ppl_like += len(result)
                    for item in result:
                        row = merge_skill_result(
                            skill_key=item["skill_key"],
                            method_updates=item["methods"],
                            records_by_skill=records_by_skill,
                            latest_rows=latest_rows,
                        )
                        append_jsonl(results_path, row)
                        persist_state()
                    log(
                        f"[ppl][model={model_name}][{completed_ppl_like}] "
                        f"finished chunk of {len(result)} skills"
                    )
        finally:
            for executor in ppl_executors:
                executor.shutdown(wait=True, cancel_futures=False)

    persist_state()
    log(
        "[done] finished run: "
        f"llm_completed={completed_llm}, llm_errors={llm_error_count}, "
        f"ppl_completed={completed_ppl_like}, ppl_errors={ppl_error_count}"
    )
    log(f"[done] summary written to: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
