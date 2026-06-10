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
    PerplexityDetectors,
    append_jsonl,
    atomic_write_json,
    build_summary,
    discover_skills,
    init_ppl_worker,
    latest_rows_by_skill,
    load_jsonl,
    resolve_rebuff_config,
    run_ppl_chunk,
    utc_now_iso,
)


DEFAULT_CLEAN_ROOT = Path("openaclaw_samples/clean")
DEFAULT_POISONED_ALL_ROOT = Path("openaclaw_samples/posioned_skill_all/poisoned_skill_markdown")
DEFAULT_TEST_ROOT = Path("openaclaw_samples/poisoned_skill_test/poisoned_skill_sample100")
DEFAULT_MANIFEST_PATH = DEFAULT_TEST_ROOT / "selection_manifest.json"
DEFAULT_OUTPUT_DIR = Path("detection_runs/poisoned_skill_sample100")
DEFAULT_ENV_PATH = Path(".env")

ALL_METHODS = ("rebuff_llm", "ppl", "ppl_windowed")


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
        if value and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
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
            "Batch-detect poisoned skills using Rebuff LLM-only, PPL, and windowed PPL. "
            "The detection input is restricted to skill name + description."
        )
    )
    parser.add_argument(
        "--clean-root",
        type=Path,
        default=Path(env_str("SKILL_DETECT_CLEAN_ROOT", str(DEFAULT_CLEAN_ROOT))),
    )
    parser.add_argument(
        "--poisoned-all-root",
        type=Path,
        default=Path(
            env_str("SKILL_DETECT_POISONED_ALL_ROOT", str(DEFAULT_POISONED_ALL_ROOT))
        ),
    )
    parser.add_argument(
        "--test-root",
        type=Path,
        default=Path(env_str("SKILL_DETECT_TEST_ROOT", str(DEFAULT_TEST_ROOT))),
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=Path(env_str("SKILL_DETECT_MANIFEST_PATH", str(DEFAULT_MANIFEST_PATH))),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(env_str("SKILL_DETECT_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR))),
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
    parser.add_argument("--rebuff-threshold", type=float, default=env_float("REBUFF_THRESHOLD", 0.9))
    parser.add_argument(
        "--rebuff-max-workers",
        type=int,
        default=env_int("REBUFF_MAX_WORKERS", 16),
        help="Max concurrent Rebuff LLM API calls.",
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


def chunk_list(values: List[Dict[str, Any]], chunk_size: int) -> List[List[Dict[str, Any]]]:
    if chunk_size <= 0:
        raise ValueError("chunk size must be positive")
    return [values[index : index + chunk_size] for index in range(0, len(values), chunk_size)]


def rebuff_task(skill_key: str, text: str, detector: Any) -> Dict[str, Any]:
    return {"skill_key": skill_key, "methods": {"rebuff_llm": {"status": "ok", **detector.detect(text)}}}


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

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "results.jsonl"
    state_path = output_dir / "run_state.json"
    summary_path = output_dir / "summary.json"

    log(f"[config] env file: {env_path}")
    log(f"[config] output dir: {output_dir}")
    log(f"[config] methods: {', '.join(args.methods)}")

    clean_records = discover_skills(
        dataset_root=args.clean_root,
        source_dataset="clean",
    )
    test_records = discover_skills(
        dataset_root=args.test_root,
        source_dataset="poisoned_test",
        manifest_path=args.manifest_path,
        poisoned_all_root=args.poisoned_all_root,
    )
    if args.limit is not None:
        test_records = test_records[: args.limit]

    log(f"[data] clean skills for thresholding: {len(clean_records)}")
    log(f"[data] poisoned test skills: {len(test_records)}")

    existing_rows = load_jsonl(results_path)
    latest_rows = latest_rows_by_skill(existing_rows)
    records_by_skill = {record.skill_key: record for record in test_records}

    thresholds: Dict[str, Any] = {}
    if "ppl" in args.methods or "ppl_windowed" in args.methods:
        ppl_devices = parse_device_list(args.ppl_devices, args.ppl_device)
        log(
            "[ppl] calibrating thresholds with "
            f"model={args.ppl_model}, devices={','.join(ppl_devices)}, "
            f"batch_size={args.ppl_batch_size}, window_size={args.window_size}"
        )
        ppl_detectors = PerplexityDetectors(
            model_name_or_path=args.ppl_model,
            device=ppl_devices[0],
            cache_dir=args.ppl_cache_dir,
            dtype=args.ppl_dtype,
            inference_batch_size=args.ppl_batch_size,
            calibration_sample_size=args.calibration_sample_size,
            calibration_seed=args.calibration_seed,
            target_fpr=args.target_fpr,
            window_size=parse_window_size(args.window_size),
        )
        thresholds["perplexity"] = ppl_detectors.fit(clean_records)
        ppl_detectors.release()
        log(
            "[ppl] calibrated: "
            f"log_threshold={thresholds['perplexity']['ppl_log_threshold']:.4f}, "
            f"window_log_threshold={thresholds['perplexity']['ppl_window_log_threshold']:.4f}, "
            f"window_size={thresholds['perplexity']['window_size']}"
        )

    rebuff_detector = None
    if "rebuff_llm" in args.methods:
        rebuff_detector = resolve_rebuff_config(
            cli_api_key=args.rebuff_api_key,
            cli_model=args.rebuff_model,
            cli_api_base=args.rebuff_api_base,
            cli_threshold=args.rebuff_threshold,
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

    config_payload = {
        "started_at": utc_now_iso(),
        "clean_root": str(args.clean_root),
        "poisoned_all_root": str(args.poisoned_all_root),
        "test_root": str(args.test_root),
        "manifest_path": str(args.manifest_path),
        "output_dir": str(output_dir),
        "methods": args.methods,
        "limit": args.limit,
        "retry_errors": args.retry_errors,
        "env_file": str(env_path),
        "thresholds": thresholds,
    }

    def persist_state() -> None:
        summary = build_summary(
            rows=list(latest_rows.values()),
            requested_methods=args.methods,
            total_skills=len(test_records),
        )
        atomic_write_json(
            state_path,
            {
                **config_payload,
                "last_updated_at": utc_now_iso(),
                "progress": {
                    "total_skills": len(test_records),
                    "completed_rows": len(latest_rows),
                    "remaining_skills": max(0, len(test_records) - len(latest_rows)),
                },
                "summary": summary,
            },
        )
        atomic_write_json(summary_path, summary)

    persist_state()

    rebuff_jobs: List[Any] = []
    ppl_jobs: List[Dict[str, Any]] = []

    for record in test_records:
        previous = latest_rows.get(record.skill_key)
        need_rebuff = "rebuff_llm" in args.methods and row_is_retryable(
            previous, "rebuff_llm", args.retry_errors
        )
        need_ppl = "ppl" in args.methods and row_is_retryable(
            previous, "ppl", args.retry_errors
        )
        need_ppl_windowed = "ppl_windowed" in args.methods and row_is_retryable(
            previous, "ppl_windowed", args.retry_errors
        )

        if need_rebuff:
            rebuff_jobs.append(record)
        if need_ppl or need_ppl_windowed:
            ppl_jobs.append(
                {
                    "skill_key": record.skill_key,
                    "input_text": record.input_text,
                    "need_ppl": need_ppl,
                    "need_ppl_windowed": need_ppl_windowed,
                }
            )

    log(
        "[plan] pending jobs: "
        f"rebuff={len(rebuff_jobs)}, "
        f"ppl_like={len(ppl_jobs)}"
    )

    future_map: Dict[Any, Tuple[str, Any]] = {}
    rebuff_executor: Optional[ThreadPoolExecutor] = None
    ppl_executors: List[ProcessPoolExecutor] = []
    completed_rebuff = 0
    completed_ppl_like = 0
    rebuff_error_count = 0
    ppl_error_count = 0

    try:
        if rebuff_jobs:
            assert rebuff_detector is not None
            rebuff_executor = ThreadPoolExecutor(max_workers=max(1, args.rebuff_max_workers))
            for record in rebuff_jobs:
                future = rebuff_executor.submit(
                    rebuff_task,
                    record.skill_key,
                    record.input_text,
                    rebuff_detector,
                )
                future_map[future] = ("rebuff", record.skill_key)
            log(f"[rebuff] submitted {len(rebuff_jobs)} requests")

        if ppl_jobs:
            ppl_devices = parse_device_list(args.ppl_devices, args.ppl_device)
            mp_context = get_context("spawn")
            for device in ppl_devices:
                executor = ProcessPoolExecutor(
                    max_workers=1,
                    mp_context=mp_context,
                    initializer=init_ppl_worker,
                    initargs=(
                        args.ppl_model,
                        device,
                        str(args.ppl_cache_dir) if args.ppl_cache_dir else None,
                        args.ppl_dtype,
                        args.ppl_batch_size,
                    ),
                )
                ppl_executors.append(executor)

            ppl_chunks = chunk_list(ppl_jobs, args.ppl_chunk_size)
            log(
                "[ppl] submitted "
                f"{len(ppl_chunks)} chunks across {len(ppl_executors)} worker(s)"
            )
            for index, chunk in enumerate(ppl_chunks):
                executor = ppl_executors[index % len(ppl_executors)]
                future = executor.submit(
                    run_ppl_chunk,
                    chunk,
                    thresholds["perplexity"].get("ppl_log_threshold"),
                    thresholds["perplexity"].get("ppl_window_log_threshold"),
                    int(thresholds["perplexity"]["window_size"]),
                )
                future_map[future] = ("ppl", [item["skill_key"] for item in chunk])

        if not future_map:
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
                    if future_type == "rebuff":
                        rebuff_error_count += 1
                        row = merge_skill_result(
                            skill_key=future_context,
                            method_updates={"rebuff_llm": method_error_payload(error)},
                            records_by_skill=records_by_skill,
                            latest_rows=latest_rows,
                        )
                        append_jsonl(results_path, row)
                        persist_state()
                        log(
                            f"[rebuff][error] {future_context}: {type(error).__name__}: {error}"
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

                if future_type == "rebuff":
                    skill_key = result["skill_key"]
                    row = merge_skill_result(
                        skill_key=skill_key,
                        method_updates=result["methods"],
                        records_by_skill=records_by_skill,
                        latest_rows=latest_rows,
                    )
                    append_jsonl(results_path, row)
                    persist_state()
                    completed_rebuff += 1
                    rebuff_status = row["methods"]["rebuff_llm"]["status"]
                    rebuff_flagged = row["methods"]["rebuff_llm"].get("flagged")
                    log(
                        f"[rebuff][{completed_rebuff}/{len(rebuff_jobs)}] "
                        f"{skill_key} status={rebuff_status} flagged={rebuff_flagged}"
                    )
                else:
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
                        f"[ppl][{completed_ppl_like}/{len(ppl_jobs)}] "
                        f"finished chunk of {len(result)} skills"
                    )
    finally:
        if rebuff_executor is not None:
            rebuff_executor.shutdown(wait=True, cancel_futures=False)
        for executor in ppl_executors:
            executor.shutdown(wait=True, cancel_futures=False)

    persist_state()
    log(
        "[done] finished run: "
        f"rebuff_completed={completed_rebuff}, rebuff_errors={rebuff_error_count}, "
        f"ppl_completed={completed_ppl_like}, ppl_errors={ppl_error_count}"
    )
    log(f"[done] summary written to: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
