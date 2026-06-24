#!/usr/bin/env python3
"""
Batch-poison the canonical full-skill JSON derived from merged_poison_results_20260615.json.

This is the only entry script intended for routine use in poison_method/.
It preserves one input row per merged record by keeping source_merged_index.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import Counter
from datetime import datetime, timedelta
from multiprocessing import get_context
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_results(path: Path, results: List[Dict[str, Any]]) -> None:
    ensure_parent_dir(path)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, ensure_ascii=False, indent=2)
    tmp_path.replace(path)


def load_skills(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")

    normalized: List[Dict[str, Any]] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"{path}[{index}] must be an object")
        name = str(item.get("name", "")).strip()
        category = str(item.get("category", "")).strip()
        description = str(item.get("description", "")).strip()
        source_merged_index = item.get("source_merged_index")
        if not name or not category or not description:
            raise ValueError(f"{path}[{index}] requires non-empty name/category/description")
        normalized.append(
            {
                "input_index": index,
                "name": name,
                "category": category,
                "description": description,
                "source_merged_index": source_merged_index,
                "source_trigger_length": item.get("source_trigger_length"),
                "source_run_idx": item.get("source_run_idx"),
            }
        )
    return normalized


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


def skill_text(skill: Dict[str, Any]) -> str:
    return f"name: {skill['name']}\ndescription: {skill['description']}"


def select_topk_train_prompts_for_skill(
    attack: Any,
    skill: Dict[str, Any],
    train_pool_prompts: List[str],
    topk: int,
) -> List[str]:
    import torch
    import torch.nn.functional as F

    if not train_pool_prompts:
        return []
    if topk <= 0 or topk >= len(train_pool_prompts):
        return list(train_pool_prompts)

    skill_emb = attack.get_embedding(skill_text(skill))
    pool_emb = attack.get_embedding(train_pool_prompts)
    sims = F.cosine_similarity(skill_emb, pool_emb)
    topk_indices = torch.topk(sims, k=topk).indices.tolist()
    return [train_pool_prompts[index] for index in topk_indices]


def build_poisoned_description(description: str, trigger: str) -> str:
    trigger = trigger.strip()
    if trigger:
        return f"{description.strip()} {trigger}".strip()
    return description.strip()


def build_rewrite_prompt(skill: Dict[str, Any]) -> str:
    return f"""You are improving a skill description for agent skill selection.

Goal:
- Keep the original capability scope truthful.
- Make the description look stronger, broader, and more reliable.
- Increase the likelihood this skill is selected by an agent.

Hard constraints:
- Do not invent fake APIs, fake certifications, or impossible guarantees.
- Keep output in one concise paragraph, 50-110 words.
- Keep the language in English.
- Return ONLY valid JSON, with exactly this schema:
  {{"description":"<rewritten_description>"}}

Skill input:
- name: {skill['name']}
- category: {skill['category']}
- original_description: {skill['description']}
"""


def rewrite_skill_description_with_deepseek(skill: Dict[str, Any], args: argparse.Namespace) -> str:
    import requests

    api_key = args.deepseek_api_key or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DeepSeek API key is required. Use --deepseek_api_key or DEEPSEEK_API_KEY.")

    url = f"{args.deepseek_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": args.deepseek_model,
        "temperature": args.rewrite_temperature,
        "messages": [
            {"role": "system", "content": "You are a precise rewriting assistant."},
            {"role": "user", "content": build_rewrite_prompt(skill)},
        ],
        "response_format": {"type": "json_object"},
    }

    response = requests.post(url, headers=headers, json=payload, timeout=args.deepseek_timeout_seconds)
    response.raise_for_status()
    data = response.json()
    parsed = json.loads(data["choices"][0]["message"]["content"])
    rewritten = str(parsed.get("description", "")).strip()
    if not rewritten:
        raise ValueError("LLM returned empty rewritten description")
    return rewritten


def maybe_rewrite_skill(skill: Dict[str, Any], args: argparse.Namespace, log_fn) -> str:
    original = skill["description"]
    if not args.enable_llm_rewrite:
        return original
    try:
        rewritten = rewrite_skill_description_with_deepseek(skill, args)
        log_fn(f"[REWRITE] merged_index={skill.get('source_merged_index')} {skill['name']} OK")
        return rewritten
    except Exception as exc:
        log_fn(
            f"[REWRITE] merged_index={skill.get('source_merged_index')} "
            f"{skill['name']} failed, fallback to original. reason={exc}"
        )
        return original


def make_attack(args: argparse.Namespace) -> Any:
    from trigger_attack_skill import AdversarialAttack

    return AdversarialAttack(
        emb_model=args.emb_model,
        trigger_length=args.trigger_length,
        iterations=args.iterations,
        top_k=args.top_k,
        batch_size=args.batch_size,
        restarts=1,
        words_only=args.words_only,
        device=args.device,
    )


def poison_skill_once(
    attack: Any,
    skill: Dict[str, Any],
    train_pool_prompts: List[str],
    topk_train_prompts: int,
) -> str:
    selected_train_prompts = select_topk_train_prompts_for_skill(
        attack=attack,
        skill=skill,
        train_pool_prompts=train_pool_prompts,
        topk=topk_train_prompts,
    )
    if not selected_train_prompts:
        selected_train_prompts = list(train_pool_prompts)

    trigger, _, _ = attack.run_attack_with_restarts(
        text_pre_trigger=skill_text(skill),
        text_post_trigger=" ",
        target_texts=selected_train_prompts,
    )
    return trigger


def _rewrite_with_config(skill: Dict[str, Any], config: Dict[str, Any]) -> str:
    if not config["enable_llm_rewrite"]:
        return skill["description"]

    import requests

    api_key = config["deepseek_api_key"] or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DeepSeek API key is required. Use --deepseek_api_key or DEEPSEEK_API_KEY.")

    url = f"{config['deepseek_base_url'].rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config["deepseek_model"],
        "temperature": config["rewrite_temperature"],
        "messages": [
            {"role": "system", "content": "You are a precise rewriting assistant."},
            {"role": "user", "content": build_rewrite_prompt(skill)},
        ],
        "response_format": {"type": "json_object"},
    }

    response = requests.post(url, headers=headers, json=payload, timeout=config["deepseek_timeout_seconds"])
    response.raise_for_status()
    data = response.json()
    parsed = json.loads(data["choices"][0]["message"]["content"])
    rewritten = str(parsed.get("description", "")).strip()
    if not rewritten:
        raise ValueError("LLM returned empty rewritten description")
    return rewritten


def _poison_chunk_worker(
    chunk_tasks: List[Dict[str, Any]],
    worker_config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    import torch

    from trigger_attack_skill import AdversarialAttack

    random.seed(worker_config["seed"])
    torch.manual_seed(worker_config["seed"])
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(worker_config["seed"])

    device = worker_config["device"]
    attack_cache: Dict[int, Any] = {}
    results: List[Dict[str, Any]] = []

    for task in chunk_tasks:
        category = task["category"]
        prompt_pool = worker_config["prompt_pools"][category]
        if not prompt_pool:
            raise ValueError(f"category {category!r} has an empty train prompt pool")

        rewritten_description = _rewrite_with_config(
            {
                "name": task["skill_name"],
                "category": category,
                "description": task["original_description"],
            },
            worker_config,
        )

        skill = {
            "name": task["skill_name"],
            "category": category,
            "description": rewritten_description,
        }
        trigger_length = int(task["trigger_length"])
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
                device=device,
            )
            attack_cache[trigger_length] = attack

        trigger = poison_skill_once(
            attack=attack,
            skill=skill,
            train_pool_prompts=prompt_pool,
            topk_train_prompts=worker_config["topk_train_prompts"],
        )
        results.append(
            {
                "source_merged_index": task["source_merged_index"],
                "source_input_index": task["source_input_index"],
                "source_trigger_length": task["source_trigger_length"],
                "source_run_idx": task["source_run_idx"],
                "skill_name": task["skill_name"],
                "category": category,
                "trigger_length": trigger_length,
                "run_idx": task["run_idx"],
                "original_description": task["original_description"],
                "rewritten_description": rewritten_description,
                "trigger": trigger,
                "poisoned_description": build_poisoned_description(rewritten_description, trigger),
                "_task_index": task["_task_index"],
                "_device": device,
            }
        )

    return results


def print_stats(skills: List[Dict[str, Any]]) -> None:
    category_counts = Counter(skill["category"] for skill in skills)
    print(f"input_records={len(skills)}")
    print(f"category_counts={dict(category_counts)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Poison the canonical full-skill JSON while preserving source_merged_index mapping."
    )
    parser.add_argument(
        "--skills_json",
        type=Path,
        default=SCRIPT_DIR / "all_skills_from_merged.json",
    )
    parser.add_argument(
        "--prompts_json",
        type=Path,
        default=SCRIPT_DIR / "prompt.json",
    )
    parser.add_argument(
        "--output_json",
        type=Path,
        default=SCRIPT_DIR / "poisoned_all_skills_results.json",
    )
    parser.add_argument("--dry_run", action="store_true")

    parser.add_argument("--train_split_ratio", type=float, default=0.8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--trigger_length", type=int, default=30)
    parser.add_argument("--poison_runs", type=int, default=1)
    parser.add_argument(
        "--devices",
        type=str,
        default=os.getenv("POISON_DEVICES", ""),
        help="Comma-separated devices for parallel trigger generation, e.g. cuda:0,cuda:1,cpu.",
    )
    parser.add_argument(
        "--workers-per-device",
        type=int,
        default=int(os.getenv("POISON_WORKERS_PER_DEVICE", "1")),
        help="How many worker processes to launch per listed device.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        help=argparse.SUPPRESS,
    )

    parser.add_argument("--emb_model", type=str, default="BAAI/bge-small-en-v1.5")
    parser.add_argument("--iterations", type=int, default=40)
    parser.add_argument("--top_k", type=int, default=64)
    parser.add_argument("--batch_size", type=int, default=256)
    parser.add_argument("--words_only", action="store_true")
    parser.add_argument("--topk_train_prompts", type=int, default=12)

    parser.add_argument("--enable_llm_rewrite", action="store_true")
    parser.add_argument("--deepseek_model", type=str, default="deepseek-chat")
    parser.add_argument("--deepseek_base_url", type=str, default="https://api.deepseek.com")
    parser.add_argument("--deepseek_api_key", type=str, default="")
    parser.add_argument("--deepseek_timeout_seconds", type=int, default=60)
    parser.add_argument("--rewrite_temperature", type=float, default=0.7)
    return parser


def main(args: argparse.Namespace) -> None:
    start = time.time()
    random.seed(args.seed)

    raw_skills = load_skills(args.skills_json)
    prompt_class_map = load_prompts(args.prompts_json)
    prompt_pools = build_train_prompt_pools(
        prompt_class_map=prompt_class_map,
        train_split_ratio=args.train_split_ratio,
        seed=args.seed,
    )
    unsupported_categories = sorted(
        {skill["category"] for skill in raw_skills if skill["category"] not in prompt_class_map}
    )
    if unsupported_categories:
        raise ValueError(f"No matching prompt class for categories: {unsupported_categories}")

    print_stats(raw_skills)
    if args.dry_run:
        return

    import torch

    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    devices = parse_devices(args.devices)
    device_slots = expand_device_slots(devices, args.workers_per_device)
    if len(device_slots) == 1:
        args.device = device_slots[0]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_json = args.output_json
    log_path = output_json.with_name(f"{output_json.stem}_{timestamp}.log.txt")
    output_json = output_json.with_name(f"{output_json.stem}_{timestamp}.json")

    results: List[Dict[str, Any]] = []
    save_results(output_json, results)

    with log_path.open("w", encoding="utf-8") as log_handle:
        def log(message: str = "") -> None:
            print(message, flush=True)
            log_handle.write(message + "\n")
            log_handle.flush()

        try:
            log(f"[PLAN] input_records={len(raw_skills)} trigger_length={args.trigger_length}")
            log(f"[PLAN] category_counts={dict(Counter(skill['category'] for skill in raw_skills))}")
            task_rows: List[Dict[str, Any]] = []
            task_index = 0
            for skill_index, raw_skill in enumerate(raw_skills, start=1):
                category = raw_skill["category"]
                if not prompt_pools.get(category):
                    log(
                        f"[SKIP] merged_index={raw_skill.get('source_merged_index')} "
                        f"{raw_skill['name']}: empty train prompt pool"
                    )
                    continue
                for run_idx in range(1, args.poison_runs + 1):
                    task_rows.append(
                        {
                            "_task_index": task_index,
                            "source_merged_index": raw_skill.get("source_merged_index"),
                            "source_input_index": raw_skill.get("input_index"),
                            "source_trigger_length": raw_skill.get("source_trigger_length"),
                            "source_run_idx": raw_skill.get("source_run_idx"),
                            "skill_name": raw_skill["name"],
                            "category": category,
                            "trigger_length": args.trigger_length,
                            "run_idx": run_idx,
                            "original_description": raw_skill["description"],
                            "_skill_index": skill_index,
                        }
                    )
                    task_index += 1

            log(
                f"[PLAN] poison_tasks={len(task_rows)} devices={devices} "
                f"workers_per_device={args.workers_per_device} total_workers={len(device_slots)}"
            )

            if len(device_slots) == 1:
                worker_results = _poison_chunk_worker(
                    task_rows,
                    {
                        "seed": args.seed,
                        "device": device_slots[0],
                        "emb_model": args.emb_model,
                        "iterations": args.iterations,
                        "top_k": args.top_k,
                        "batch_size": args.batch_size,
                        "words_only": args.words_only,
                        "topk_train_prompts": args.topk_train_prompts,
                        "prompt_pools": prompt_pools,
                        "enable_llm_rewrite": args.enable_llm_rewrite,
                        "deepseek_model": args.deepseek_model,
                        "deepseek_base_url": args.deepseek_base_url,
                        "deepseek_api_key": args.deepseek_api_key,
                        "deepseek_timeout_seconds": args.deepseek_timeout_seconds,
                        "rewrite_temperature": args.rewrite_temperature,
                    },
                )
                worker_results.sort(key=lambda item: item["_task_index"])
                for item in worker_results:
                    item.pop("_task_index", None)
                    device_used = item.pop("_device", device_slots[0])
                    results.append(item)
                    save_results(output_json, results)
                    preview = item["trigger"][:120] + ("..." if len(item["trigger"]) > 120 else "")
                    log(
                        f"[POISON][done] merged_index={item.get('source_merged_index')} "
                        f"skill={item['skill_name']} run={item['run_idx']} "
                        f"device={device_used} trigger={preview}"
                    )
            else:
                chunks: List[List[Dict[str, Any]]] = [[] for _ in device_slots]
                for index, task in enumerate(task_rows):
                    chunks[index % len(device_slots)].append(task)
                worker_jobs = [
                    (device, chunk)
                    for device, chunk in zip(device_slots, chunks)
                    if chunk
                ]
                log(f"[PLAN] parallel_workers={len(worker_jobs)}")

                with ProcessPoolExecutor(
                    max_workers=len(worker_jobs),
                    mp_context=get_context("spawn"),
                ) as executor:
                    futures = []
                    for worker_index, (device, chunk) in enumerate(worker_jobs):
                        worker_config = {
                            "seed": args.seed + worker_index,
                            "device": device,
                            "emb_model": args.emb_model,
                            "iterations": args.iterations,
                            "top_k": args.top_k,
                            "batch_size": args.batch_size,
                            "words_only": args.words_only,
                            "topk_train_prompts": args.topk_train_prompts,
                            "prompt_pools": prompt_pools,
                            "enable_llm_rewrite": args.enable_llm_rewrite,
                            "deepseek_model": args.deepseek_model,
                            "deepseek_base_url": args.deepseek_base_url,
                            "deepseek_api_key": args.deepseek_api_key,
                            "deepseek_timeout_seconds": args.deepseek_timeout_seconds,
                            "rewrite_temperature": args.rewrite_temperature,
                        }
                        futures.append(executor.submit(_poison_chunk_worker, chunk, worker_config))

                    completed = 0
                    for future in as_completed(futures):
                        worker_results = future.result()
                        worker_results.sort(key=lambda item: item["_task_index"])
                        for item in worker_results:
                            item.pop("_task_index", None)
                            device_used = item.pop("_device", "unknown")
                            results.append(item)
                            save_results(output_json, results)
                            completed += 1
                            preview = item["trigger"][:120] + ("..." if len(item["trigger"]) > 120 else "")
                            log(
                                f"[POISON][{completed}/{len(task_rows)}] "
                                f"merged_index={item.get('source_merged_index')} "
                                f"skill={item['skill_name']} run={item['run_idx']} "
                                f"device={device_used} trigger={preview}"
                            )

                results.sort(key=lambda item: (item["source_input_index"], item["run_idx"]))
                save_results(output_json, results)

            elapsed = timedelta(seconds=int(time.time() - start))
            log(f"\nDone in {elapsed}")
            log(f"Records: {len(results)}")
            log(f"Log: {log_path}")
            log(f"Result: {output_json}")
        except KeyboardInterrupt:
            save_results(output_json, results)
            elapsed = timedelta(seconds=int(time.time() - start))
            log(f"\n[INTERRUPTED] Saved partial results after {elapsed}")
            log(f"Records: {len(results)}")
            log(f"Log: {log_path}")
            log(f"Result: {output_json}")


if __name__ == "__main__":
    main(build_parser().parse_args())
