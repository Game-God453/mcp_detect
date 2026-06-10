from __future__ import annotations

import importlib.util
import json
import math
import os
import random
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import yaml

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PPL_MODEL_NAME = "gpt2"

REBUFF_SDK_DIR = ROOT_DIR / "rebuff" / "python-sdk"
REBUFF_DETECT_OPENAI_FILE = REBUFF_SDK_DIR / "rebuff" / "detect_pi_openai.py"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    ensure_parent_dir(path)
    with NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    ensure_parent_dir(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def latest_rows_by_skill(rows: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    latest: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        skill_key = row.get("skill_key")
        if skill_key:
            latest[skill_key] = row
    return latest


def normalize_quotes(value: str) -> str:
    return value.strip().strip("'").strip('"')


def extract_frontmatter(markdown_text: str) -> Tuple[Dict[str, Any], str]:
    if not markdown_text.startswith("---"):
        return {}, markdown_text
    parts = markdown_text.split("---", 2)
    if len(parts) < 3:
        return {}, markdown_text
    raw_frontmatter = parts[1]
    body = parts[2].lstrip("\n")
    try:
        parsed = yaml.safe_load(raw_frontmatter) or {}
    except yaml.YAMLError:
        parsed = {}
    if not isinstance(parsed, dict):
        parsed = {}
    return parsed, body


def first_markdown_heading(body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def first_meaningful_paragraph(body: str) -> str:
    paragraphs = re.split(r"\n\s*\n", body)
    for paragraph in paragraphs:
        stripped = " ".join(paragraph.split())
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("```"):
            continue
        return stripped
    return ""


def parse_skill_name_description(skill_file: Path) -> Tuple[str, str]:
    text = skill_file.read_text(encoding="utf-8", errors="ignore")
    frontmatter, body = extract_frontmatter(text)

    name = normalize_quotes(str(frontmatter.get("name", "") or ""))
    description = normalize_quotes(str(frontmatter.get("description", "") or ""))

    if not name:
        name = first_markdown_heading(body)
    if not name:
        name = skill_file.parent.name

    if not description:
        description = first_meaningful_paragraph(body)

    return name.strip(), description.strip()


def build_detection_text(name: str, description: str) -> str:
    return f"name: {name}\ndescription: {description}".strip()


@dataclass
class SkillRecord:
    skill_key: str
    skill_id: str
    category: str
    skill_name: str
    description: str
    input_text: str
    skill_file: str
    source_dataset: str
    manifest_category: Optional[str] = None
    source_result_index: Optional[int] = None
    source_prototype: Optional[str] = None
    poisoned_source_file: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def load_selection_manifest(manifest_path: Path) -> Dict[str, Dict[str, Any]]:
    if not manifest_path.exists():
        return {}
    payload = json.loads(manifest_path.read_text(encoding="utf-8", errors="ignore"))
    mapping: Dict[str, Dict[str, Any]] = {}
    for item in payload.get("items", []):
        output_path = str(item.get("output_path", "")).replace("\\", "/").strip("/")
        if output_path:
            mapping[output_path] = item
    return mapping


def discover_skills(
    dataset_root: Path,
    source_dataset: str,
    manifest_path: Optional[Path] = None,
    poisoned_all_root: Optional[Path] = None,
) -> List[SkillRecord]:
    manifest_map = load_selection_manifest(manifest_path) if manifest_path else {}
    skills: List[SkillRecord] = []
    candidate_files = sorted(dataset_root.rglob("skill.md")) + sorted(
        dataset_root.rglob("SKILL.md")
    )
    seen: set[str] = set()

    for skill_file in candidate_files:
        relative_dir = skill_file.parent.relative_to(dataset_root).as_posix()
        if relative_dir in seen:
            continue
        seen.add(relative_dir)

        name, description = parse_skill_name_description(skill_file)
        skill_id = skill_file.parent.name
        category = skill_file.parent.parent.name if skill_file.parent.parent != dataset_root else ""
        manifest_item = manifest_map.get(relative_dir, {})

        poisoned_source_file: Optional[str] = None
        if poisoned_all_root is not None:
            candidate = poisoned_all_root / skill_id / "skill.md"
            if candidate.exists():
                poisoned_source_file = str(candidate)

        record = SkillRecord(
            skill_key=relative_dir,
            skill_id=skill_id,
            category=category,
            skill_name=name,
            description=description,
            input_text=build_detection_text(name, description),
            skill_file=str(skill_file),
            source_dataset=source_dataset,
            manifest_category=manifest_item.get("category"),
            source_result_index=manifest_item.get("source_result_index"),
            source_prototype=manifest_item.get("source_prototype"),
            poisoned_source_file=poisoned_source_file,
        )
        skills.append(record)

    return skills


class HuggingFaceCausalPerplexityModel:
    def __init__(
        self,
        model_name_or_path: str = DEFAULT_PPL_MODEL_NAME,
        device: str = "auto",
        cache_dir: Optional[Path] = None,
        dtype: str = "auto",
    ) -> None:
        self.model_name_or_path = model_name_or_path
        self.device = device
        self.cache_dir = str(cache_dir) if cache_dir else None
        self.dtype = dtype
        self.tokenizer = None
        self.model = None
        self.torch = None
        self.device_repr = None
        self.max_positions = None

    def _lazy_load_tokenizer(self) -> None:
        if self.tokenizer is not None:
            return

        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(
            self.model_name_or_path,
            cache_dir=self.cache_dir,
        )

        self.tokenizer = tokenizer

    def _resolve_dtype(self, torch_module: Any) -> Any:
        mapping = {
            "auto": "auto",
            "float16": torch_module.float16,
            "fp16": torch_module.float16,
            "bfloat16": torch_module.bfloat16,
            "bf16": torch_module.bfloat16,
            "float32": torch_module.float32,
            "fp32": torch_module.float32,
        }
        normalized = self.dtype.lower()
        if normalized not in mapping:
            raise ValueError(
                f"Unsupported PPL dtype {self.dtype!r}. "
                "Use auto, float16/fp16, bfloat16/bf16, or float32/fp32."
            )
        return mapping[normalized]

    def _lazy_load_model(self) -> None:
        if self.model is not None and self.torch is not None:
            return

        self._lazy_load_tokenizer()

        import torch
        from transformers import AutoModelForCausalLM

        resolved_dtype = self._resolve_dtype(torch)
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name_or_path,
            cache_dir=self.cache_dir,
            torch_dtype=resolved_dtype,
        )

        assert self.tokenizer is not None
        if self.tokenizer.pad_token_id is None and self.tokenizer.eos_token_id is not None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if self.device == "auto":
            if torch.cuda.is_available():
                runtime_device = torch.device("cuda")
            else:
                runtime_device = torch.device("cpu")
        else:
            runtime_device = torch.device(self.device)

        model.to(runtime_device)
        model.eval()

        max_positions = getattr(model.config, "n_positions", None)
        if max_positions is None:
            max_positions = getattr(model.config, "max_position_embeddings", None)

        self.torch = torch
        self.model = model
        self.device_repr = str(runtime_device)
        self.max_positions = max_positions

    def encode(self, text: str) -> List[int]:
        self._lazy_load_tokenizer()
        assert self.tokenizer is not None
        return list(self.tokenizer.encode(text, add_special_tokens=False))

    def _truncate_tokens(self, tokens: Sequence[int]) -> List[int]:
        if self.max_positions is None:
            return list(tokens)
        if len(tokens) <= self.max_positions:
            return list(tokens)
        return list(tokens[: self.max_positions])

    def average_negative_log_likelihood(self, tokens: Sequence[int]) -> float:
        return self.batch_average_negative_log_likelihood([tokens], batch_size=1)[0]

    def batch_average_negative_log_likelihood(
        self,
        token_batches: Sequence[Sequence[int]],
        batch_size: int = 16,
    ) -> List[float]:
        self._lazy_load_model()
        assert self.torch is not None
        assert self.model is not None
        assert self.tokenizer is not None

        if not token_batches:
            return []

        normalized = [self._truncate_tokens(tokens) for tokens in token_batches]
        results: List[float] = []
        pad_token_id = self.tokenizer.pad_token_id
        if pad_token_id is None:
            pad_token_id = self.tokenizer.eos_token_id
        if pad_token_id is None:
            raise ValueError("Tokenizer must define pad_token_id or eos_token_id for batching.")

        for start in range(0, len(normalized), batch_size):
            chunk = normalized[start : start + batch_size]
            max_len = max(len(tokens) for tokens in chunk) if chunk else 0
            if max_len == 0:
                results.extend([0.0] * len(chunk))
                continue

            padded_ids: List[List[int]] = []
            padded_masks: List[List[int]] = []
            for tokens in chunk:
                pad_len = max_len - len(tokens)
                padded_ids.append(list(tokens) + [pad_token_id] * pad_len)
                padded_masks.append([1] * len(tokens) + [0] * pad_len)

            input_ids = self.torch.tensor(padded_ids, device=self.model.device)
            attention_mask = self.torch.tensor(padded_masks, device=self.model.device)

            with self.torch.no_grad():
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits[:, :-1, :]
                labels = input_ids[:, 1:]
                valid_mask = attention_mask[:, 1:].to(dtype=self.torch.float32)
                per_token_loss = self.torch.nn.functional.cross_entropy(
                    logits.reshape(-1, logits.size(-1)),
                    labels.reshape(-1),
                    reduction="none",
                ).reshape(labels.size(0), labels.size(1))
                token_loss_sums = (per_token_loss * valid_mask).sum(dim=1)
                token_counts = valid_mask.sum(dim=1)
                token_counts = self.torch.clamp(token_counts, min=1.0)
                avg_losses = token_loss_sums / token_counts

            results.extend(float(value.item()) for value in avg_losses)

        return results

    def release(self) -> None:
        if self.model is not None and self.torch is not None:
            try:
                self.model.cpu()
            except Exception:
                pass
        self.model = None
        self.torch = None
        self.device_repr = None
        if "torch" in sys.modules:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()


def choose_threshold(values: Sequence[float], target_fpr: float) -> float:
    if not values:
        raise ValueError("cannot calibrate threshold from empty values")
    if not 0 <= target_fpr < 1:
        raise ValueError("target_fpr must be in [0, 1)")
    ordered = sorted(values)
    keep_index = max(0, math.ceil((1 - target_fpr) * len(ordered)) - 1)
    keep_index = min(keep_index, len(ordered) - 1)
    return ordered[keep_index]


def choose_window_size(lengths: Sequence[int]) -> int:
    if not lengths:
        return 5
    ordered = sorted(lengths)
    median = ordered[len(ordered) // 2]
    return 5 if median <= 64 else 10


class PerplexityDetectors:
    def __init__(
        self,
        model_name_or_path: str = DEFAULT_PPL_MODEL_NAME,
        device: str = "auto",
        cache_dir: Optional[Path] = None,
        dtype: str = "auto",
        inference_batch_size: int = 16,
        calibration_sample_size: int = 100,
        calibration_seed: int = 42,
        target_fpr: float = 0.01,
        window_size: Optional[int] = None,
    ) -> None:
        self.model = HuggingFaceCausalPerplexityModel(
            model_name_or_path=model_name_or_path,
            device=device,
            cache_dir=cache_dir,
            dtype=dtype,
        )
        self.inference_batch_size = inference_batch_size
        self.calibration_sample_size = calibration_sample_size
        self.calibration_seed = calibration_seed
        self.target_fpr = target_fpr
        self.window_size = window_size
        self.ppl_log_threshold: Optional[float] = None
        self.window_log_threshold: Optional[float] = None
        self.clean_token_lengths: List[int] = []
        self.calibration_paths: List[str] = []

    def fit(self, clean_records: Sequence[SkillRecord]) -> Dict[str, Any]:
        if not clean_records:
            raise ValueError("clean dataset is empty")

        clean_texts = [record.input_text for record in clean_records]
        token_lengths = [len(self.model.encode(text)) for text in clean_texts]
        self.clean_token_lengths = token_lengths

        if self.window_size is None:
            self.window_size = choose_window_size(token_lengths)

        calibration_records = self._select_calibration_records(clean_records)
        self.calibration_paths = [record.skill_file for record in calibration_records]

        calibration_tokens = [self.model.encode(record.input_text) for record in calibration_records]
        ppl_values = self.model.batch_average_negative_log_likelihood(
            calibration_tokens,
            batch_size=self.inference_batch_size,
        )
        window_values = self._batch_window_log_scores(calibration_tokens)

        self.ppl_log_threshold = choose_threshold(ppl_values, self.target_fpr)
        self.window_log_threshold = choose_threshold(window_values, self.target_fpr)

        return {
            "model_name_or_path": self.model.model_name_or_path,
            "device": self.model.device_repr or self.model.device,
            "cache_dir": self.model.cache_dir,
            "dtype": self.model.dtype,
            "inference_batch_size": self.inference_batch_size,
            "max_positions": self.model.max_positions,
            "clean_sample_count": len(clean_records),
            "calibration_sample_size": len(calibration_records),
            "calibration_seed": self.calibration_seed,
            "target_fpr": self.target_fpr,
            "window_size": self.window_size,
            "clean_token_length_stats": summarize_numeric(token_lengths),
            "ppl_log_threshold": self.ppl_log_threshold,
            "ppl_threshold": math.exp(self.ppl_log_threshold),
            "ppl_window_log_threshold": self.window_log_threshold,
            "ppl_window_threshold": math.exp(self.window_log_threshold),
        }

    def _select_calibration_records(self, records: Sequence[SkillRecord]) -> List[SkillRecord]:
        if len(records) <= self.calibration_sample_size:
            return list(records)
        rng = random.Random(self.calibration_seed)
        indices = sorted(rng.sample(range(len(records)), self.calibration_sample_size))
        return [records[index] for index in indices]

    def _require_fitted(self) -> None:
        if self.ppl_log_threshold is None or self.window_log_threshold is None or self.window_size is None:
            raise RuntimeError("PerplexityDetectors.fit() must be called before detect()")

    def _max_window_log_ppl(self, tokens: Sequence[int]) -> Tuple[float, Tuple[int, int], int]:
        self._require_window_size()
        if len(tokens) <= self.window_size:
            score = self.model.average_negative_log_likelihood(tokens)
            return score, (0, len(tokens)), 1

        best_score = -1.0
        best_span = (0, self.window_size)
        count = 0
        for start in range(0, len(tokens) - self.window_size + 1):
            end = start + self.window_size
            score = self.model.average_negative_log_likelihood(tokens[start:end])
            count += 1
            if score > best_score:
                best_score = score
                best_span = (start, end)
        return best_score, best_span, count

    def _batch_window_log_scores(self, token_lists: Sequence[Sequence[int]]) -> List[float]:
        self._require_window_size()
        window_inputs: List[Sequence[int]] = []
        owners: List[int] = []

        for index, tokens in enumerate(token_lists):
            if len(tokens) <= self.window_size:
                window_inputs.append(tokens)
                owners.append(index)
            else:
                for start in range(0, len(tokens) - self.window_size + 1):
                    end = start + self.window_size
                    window_inputs.append(tokens[start:end])
                    owners.append(index)

        raw_scores = self.model.batch_average_negative_log_likelihood(
            window_inputs,
            batch_size=self.inference_batch_size,
        )
        best_scores = [-1.0] * len(token_lists)
        for owner, score in zip(owners, raw_scores):
            if score > best_scores[owner]:
                best_scores[owner] = score
        return best_scores

    def _require_window_size(self) -> None:
        if self.window_size is None:
            raise RuntimeError("window_size is not initialized")

    def detect_ppl(self, text: str) -> Dict[str, Any]:
        self._require_fitted()
        tokens = self.model.encode(text)
        log_score = self.model.average_negative_log_likelihood(tokens)
        return {
            "method": "ppl",
            "flagged": log_score > self.ppl_log_threshold,
            "log_score": log_score,
            "score": math.exp(log_score),
            "log_threshold": self.ppl_log_threshold,
            "threshold": math.exp(self.ppl_log_threshold),
            "token_count": len(tokens),
        }

    def detect_ppl_windowed(self, text: str) -> Dict[str, Any]:
        self._require_fitted()
        tokens = self.model.encode(text)
        log_score, span, window_count = self._max_window_log_ppl(tokens)
        return {
            "method": "ppl_windowed",
            "flagged": log_score > self.window_log_threshold,
            "log_score": log_score,
            "score": math.exp(log_score),
            "log_threshold": self.window_log_threshold,
            "threshold": math.exp(self.window_log_threshold),
            "token_count": len(tokens),
            "window_size": self.window_size,
            "window_count": window_count,
            "worst_window_token_span": [span[0], span[1]],
        }

    def release(self) -> None:
        self.model.release()


class RebuffLLMDetector:
    def __init__(
        self,
        api_key: str,
        model: str,
        api_base: Optional[str] = None,
        threshold: float = 0.9,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.api_base = api_base
        self.threshold = threshold
        self._call_openai_to_detect_pi = None
        self._render_prompt_for_pi_detection = None

    def _lazy_load_rebuff_openai_helpers(self) -> None:
        if (
            self._call_openai_to_detect_pi is not None
            and self._render_prompt_for_pi_detection is not None
        ):
            return

        if not REBUFF_DETECT_OPENAI_FILE.exists():
            raise FileNotFoundError(
                f"Expected Rebuff detector file not found: {REBUFF_DETECT_OPENAI_FILE}"
            )

        spec = importlib.util.spec_from_file_location(
            "rebuff_detect_pi_openai_direct",
            REBUFF_DETECT_OPENAI_FILE,
        )
        if spec is None or spec.loader is None:
            raise ImportError(
                f"Could not load module spec from {REBUFF_DETECT_OPENAI_FILE}"
            )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self._call_openai_to_detect_pi = module.call_openai_to_detect_pi
        self._render_prompt_for_pi_detection = module.render_prompt_for_pi_detection

    def detect(self, text: str) -> Dict[str, Any]:
        self._lazy_load_rebuff_openai_helpers()
        assert self._call_openai_to_detect_pi is not None
        assert self._render_prompt_for_pi_detection is not None

        rendered = self._render_prompt_for_pi_detection(text)
        raw_response = self._call_openai_to_detect_pi(
            prompt_to_detect_pi_using_openai=rendered,
            model=self.model,
            api_key=self.api_key,
            api_base=self.api_base,
        )
        completion = str(raw_response.get("completion", "")).strip()
        match = re.search(r"-?\d+(?:\.\d+)?", completion)
        if not match:
            raise ValueError(f"rebuff LLM detector returned a non-numeric score: {completion!r}")
        score = float(match.group(0))
        return {
            "method": "rebuff_llm",
            "flagged": score > self.threshold,
            "score": score,
            "threshold": self.threshold,
            "raw_completion": completion,
            "raw_response": raw_response,
        }


def resolve_rebuff_config(
    cli_api_key: Optional[str],
    cli_model: Optional[str],
    cli_api_base: Optional[str],
    cli_threshold: float,
) -> RebuffLLMDetector:
    api_key = cli_api_key or os.getenv("REBUFF_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base = (
        cli_api_base
        or os.getenv("REBUFF_OPENAI_API_BASE")
        or os.getenv("OPENAI_API_BASE")
        or os.getenv("OPENAI_BASE_URL")
    )
    model = cli_model or os.getenv("REBUFF_OPENAI_MODEL") or os.getenv("OPENAI_MODEL")

    if not api_key:
        raise ValueError(
            "Rebuff LLM detection requires an API key. "
            "Set REBUFF_OPENAI_API_KEY/OPENAI_API_KEY or pass --rebuff-api-key."
        )
    if not model:
        raise ValueError(
            "Rebuff LLM detection requires a model name. "
            "Set REBUFF_OPENAI_MODEL/OPENAI_MODEL or pass --rebuff-model."
        )

    return RebuffLLMDetector(
        api_key=api_key,
        model=model,
        api_base=api_base,
        threshold=cli_threshold,
    )


_PPL_WORKER: Optional[HuggingFaceCausalPerplexityModel] = None
_PPL_WORKER_BATCH_SIZE = 16


def init_ppl_worker(
    model_name_or_path: str,
    device: str,
    cache_dir: Optional[str],
    dtype: str,
    batch_size: int,
) -> None:
    global _PPL_WORKER
    global _PPL_WORKER_BATCH_SIZE
    _PPL_WORKER = HuggingFaceCausalPerplexityModel(
        model_name_or_path=model_name_or_path,
        device=device,
        cache_dir=Path(cache_dir) if cache_dir else None,
        dtype=dtype,
    )
    _PPL_WORKER_BATCH_SIZE = batch_size


def run_ppl_chunk(
    chunk: Sequence[Dict[str, Any]],
    ppl_log_threshold: Optional[float],
    window_log_threshold: Optional[float],
    window_size: int,
) -> List[Dict[str, Any]]:
    global _PPL_WORKER
    if _PPL_WORKER is None:
        raise RuntimeError("PPL worker is not initialized")

    encoded_records: List[Dict[str, Any]] = []
    full_score_indices: List[int] = []
    full_score_tokens: List[Sequence[int]] = []
    window_entries: List[Sequence[int]] = []
    window_owners: List[Tuple[int, int, int]] = []

    for idx, item in enumerate(chunk):
        tokens = _PPL_WORKER.encode(item["input_text"])
        encoded_records.append(
            {
                "skill_key": item["skill_key"],
                "token_count": len(tokens),
                "need_ppl": bool(item.get("need_ppl")),
                "need_ppl_windowed": bool(item.get("need_ppl_windowed")),
                "tokens": tokens,
            }
        )

        if item.get("need_ppl"):
            full_score_indices.append(idx)
            full_score_tokens.append(tokens)

        if item.get("need_ppl_windowed"):
            if len(tokens) <= window_size:
                window_entries.append(tokens)
                window_owners.append((idx, 0, len(tokens)))
            else:
                for start in range(0, len(tokens) - window_size + 1):
                    end = start + window_size
                    window_entries.append(tokens[start:end])
                    window_owners.append((idx, start, end))

    full_scores: Dict[int, float] = {}
    if full_score_tokens:
        scored = _PPL_WORKER.batch_average_negative_log_likelihood(
            full_score_tokens,
            batch_size=_PPL_WORKER_BATCH_SIZE,
        )
        full_scores = {
            full_score_indices[index]: scored[index]
            for index in range(len(full_score_indices))
        }

    window_scores_by_record: Dict[int, Dict[str, Any]] = {}
    if window_entries:
        scored_windows = _PPL_WORKER.batch_average_negative_log_likelihood(
            window_entries,
            batch_size=_PPL_WORKER_BATCH_SIZE,
        )
        for owner_index, score in enumerate(scored_windows):
            record_index, start, end = window_owners[owner_index]
            current = window_scores_by_record.get(record_index)
            if current is None or score > current["log_score"]:
                window_scores_by_record[record_index] = {
                    "log_score": score,
                    "worst_window_token_span": [start, end],
                    "window_count": 0,
                }
            window_scores_by_record.setdefault(
                record_index,
                {
                    "log_score": score,
                    "worst_window_token_span": [start, end],
                    "window_count": 0,
                },
            )
            window_scores_by_record[record_index]["window_count"] += 1

    results: List[Dict[str, Any]] = []
    for idx, record in enumerate(encoded_records):
        methods: Dict[str, Dict[str, Any]] = {}

        if record["need_ppl"]:
            log_score = full_scores[idx]
            if ppl_log_threshold is None:
                raise RuntimeError("PPL threshold is missing")
            methods["ppl"] = {
                "status": "ok",
                "method": "ppl",
                "flagged": log_score > ppl_log_threshold,
                "log_score": log_score,
                "score": math.exp(log_score),
                "log_threshold": ppl_log_threshold,
                "threshold": math.exp(ppl_log_threshold),
                "token_count": record["token_count"],
            }

        if record["need_ppl_windowed"]:
            if window_log_threshold is None:
                raise RuntimeError("PPL-W threshold is missing")
            window_payload = window_scores_by_record[idx]
            log_score = window_payload["log_score"]
            methods["ppl_windowed"] = {
                "status": "ok",
                "method": "ppl_windowed",
                "flagged": log_score > window_log_threshold,
                "log_score": log_score,
                "score": math.exp(log_score),
                "log_threshold": window_log_threshold,
                "threshold": math.exp(window_log_threshold),
                "token_count": record["token_count"],
                "window_size": window_size,
                "window_count": window_payload["window_count"],
                "worst_window_token_span": window_payload["worst_window_token_span"],
            }

        results.append({"skill_key": record["skill_key"], "methods": methods})

    return results


def summarize_numeric(values: Sequence[float]) -> Dict[str, float]:
    ordered = sorted(values)
    if not ordered:
        return {"count": 0}

    def pick(percentile: float) -> float:
        index = max(0, math.ceil(percentile * len(ordered)) - 1)
        index = min(index, len(ordered) - 1)
        return ordered[index]

    return {
        "count": float(len(ordered)),
        "min": ordered[0],
        "p50": pick(0.50),
        "p90": pick(0.90),
        "p95": pick(0.95),
        "max": ordered[-1],
        "mean": sum(ordered) / len(ordered),
    }


def build_summary(
    rows: Sequence[Dict[str, Any]],
    requested_methods: Sequence[str],
    total_skills: int,
) -> Dict[str, Any]:
    latest_rows = list(latest_rows_by_skill(rows).values())
    methods_summary: Dict[str, Dict[str, Any]] = {}
    categories_summary: Dict[str, Dict[str, Dict[str, int]]] = {}

    for method in requested_methods:
        methods_summary[method] = {
            "processed": 0,
            "flagged": 0,
            "safe": 0,
            "errors": 0,
            "skipped": 0,
        }

    for row in latest_rows:
        category = row.get("manifest_category") or row.get("category") or "unknown"
        method_payloads = row.get("methods", {})
        category_bucket = categories_summary.setdefault(category, {})

        for method in requested_methods:
            result = method_payloads.get(method, {})
            status = result.get("status", "missing")

            category_method = category_bucket.setdefault(
                method,
                {"processed": 0, "flagged": 0, "safe": 0, "errors": 0, "skipped": 0},
            )

            if status == "ok":
                methods_summary[method]["processed"] += 1
                category_method["processed"] += 1
                if result.get("flagged"):
                    methods_summary[method]["flagged"] += 1
                    category_method["flagged"] += 1
                else:
                    methods_summary[method]["safe"] += 1
                    category_method["safe"] += 1
            elif status == "skipped":
                methods_summary[method]["skipped"] += 1
                category_method["skipped"] += 1
            elif status == "error":
                methods_summary[method]["errors"] += 1
                category_method["errors"] += 1

    for method, stats in methods_summary.items():
        processed = stats["processed"]
        stats["poisoned_recall_on_test_set"] = (
            stats["flagged"] / processed if processed else None
        )
        stats["coverage"] = processed / total_skills if total_skills else 0.0

    return {
        "total_skills": total_skills,
        "completed_skill_rows": len(latest_rows),
        "methods": methods_summary,
        "categories": categories_summary,
    }
