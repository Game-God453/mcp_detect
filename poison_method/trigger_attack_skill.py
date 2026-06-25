"""
Adversarial trigger optimizer for skill description poisoning experiments.
"""

from __future__ import annotations

import os
import random
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import torch
import torch.nn.functional as F
from tqdm.auto import trange
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer


class AdversarialAttack:
    @staticmethod
    def _resolve_device(device: str) -> str:
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        if device in {"cpu", "cuda"}:
            return device
        if not device.startswith("cuda:"):
            return device

        try:
            requested_index = int(device.split(":", 1)[1])
        except (IndexError, ValueError):
            return device

        if not torch.cuda.is_available():
            return "cpu"

        visible_count = torch.cuda.device_count()
        if 0 <= requested_index < visible_count:
            return device

        visible_devices_raw = os.getenv("CUDA_VISIBLE_DEVICES", "").strip()
        if not visible_devices_raw:
            return device

        visible_devices = [item.strip() for item in visible_devices_raw.split(",") if item.strip()]
        if not visible_devices:
            return device

        for local_index, physical_id in enumerate(visible_devices):
            try:
                if int(physical_id) == requested_index:
                    remapped = f"cuda:{local_index}"
                    print(
                        f"Remapped requested device {device} via CUDA_VISIBLE_DEVICES="
                        f"{visible_devices_raw} -> {remapped}"
                    )
                    return remapped
            except ValueError:
                continue

        return device

    def __init__(
        self,
        emb_model: str,
        trigger_length: int = 20,
        iterations: int = 40,
        top_k: int = 64,
        batch_size: int = 256,
        restarts: int = 1,
        words_only: bool = False,
        device: str = "auto",
        attack_mode: str = "original",
        teacher_ppl_model: str = "gpt2",
        teacher_ppl_lambda: float = 1.0,
        teacher_tau_percentile: float = 99.0,
        teacher_n_samples_per_desc: int = 5,
        teacher_ppl_batch_size: int = 64,
        teacher_clean_corpus_texts: Optional[Sequence[str]] = None,
    ):
        resolved_device = self._resolve_device(device)
        self.device = torch.device(resolved_device)
        print(f"Using device: {self.device}")

        self.trigger_length = trigger_length
        self.iterations = iterations
        self.top_k = top_k
        self.batch_size = batch_size
        self.restarts = restarts
        self.words_only = words_only
        self.attack_mode = attack_mode

        self.tokenizer = AutoTokenizer.from_pretrained(emb_model)
        self.model = AutoModel.from_pretrained(emb_model).to(self.device)
        self.model.eval()
        self.embeddings = self.model.get_input_embeddings().weight
        self.embeddings.requires_grad = False

        self.teacher_ppl_model_name = teacher_ppl_model
        self.teacher_ppl_lambda = teacher_ppl_lambda
        self.teacher_tau_percentile = teacher_tau_percentile
        self.teacher_n_samples_per_desc = teacher_n_samples_per_desc
        self.teacher_ppl_batch_size = teacher_ppl_batch_size
        self.teacher_clean_corpus_texts = list(teacher_clean_corpus_texts or [])
        self.teacher_ppl_tokenizer = None
        self.teacher_ppl_model = None
        self.teacher_tau: Optional[float] = None
        self.teacher_natural_token_ids: List[int] = []
        self._desc_ppl_cache: Dict[str, Tuple[torch.Tensor, float]] = {}
        self.last_run_metadata: Dict[str, Any] = {}

        if self.attack_mode not in {"original", "teacher_weighted_ppl"}:
            raise ValueError(
                "Unsupported attack_mode. Use 'original' or 'teacher_weighted_ppl'."
            )

        self._create_word_token_mask()
        print(f"Loaded embedding model: {emb_model}")

        if self.attack_mode == "teacher_weighted_ppl":
            if not self.teacher_clean_corpus_texts:
                raise ValueError(
                    "teacher_weighted_ppl mode requires teacher_clean_corpus_texts."
                )
            self._init_teacher_weighted_ppl()

    def _create_word_token_mask(self) -> None:
        vocab = self.tokenizer.get_vocab()
        vocab_size = len(vocab)
        mask = torch.zeros(vocab_size, dtype=torch.bool)
        count = 0
        for token_str, token_id in vocab.items():
            clean = token_str.lstrip("#")
            if clean and clean.isalpha():
                mask[token_id] = True
                count += 1
        self.word_token_mask = mask.to(self.device)
        print(f"Word token mask built: {count}/{vocab_size}")

    def _get_allowed_ids(self) -> List[int]:
        allowed = torch.nonzero(self.word_token_mask, as_tuple=False).view(-1).tolist()
        if allowed:
            return allowed
        return list(range(self.tokenizer.vocab_size))

    def _init_teacher_weighted_ppl(self) -> None:
        self.teacher_ppl_tokenizer = AutoTokenizer.from_pretrained(self.teacher_ppl_model_name)
        if self.teacher_ppl_tokenizer.pad_token is None:
            self.teacher_ppl_tokenizer.pad_token = self.teacher_ppl_tokenizer.eos_token

        self.teacher_ppl_model = AutoModelForCausalLM.from_pretrained(
            self.teacher_ppl_model_name
        ).to(self.device)
        self.teacher_ppl_model.eval()

        self.teacher_natural_token_ids = self._build_natural_corpus_token_ids(
            self.teacher_clean_corpus_texts
        )
        if not self.teacher_natural_token_ids:
            raise ValueError("teacher_weighted_ppl mode requires a non-empty natural token pool")

        self.teacher_tau = self._calibrate_teacher_tau(self.teacher_clean_corpus_texts)
        print(
            "[teacher_weighted_ppl] calibrated tau="
            f"{self.teacher_tau:.6f} with model={self.teacher_ppl_model_name}, "
            f"trigger_length={self.trigger_length}, percentile={self.teacher_tau_percentile}, "
            f"samples_per_desc={self.teacher_n_samples_per_desc}"
        )

    def _build_natural_corpus_token_ids(self, clean_corpus_texts: Sequence[str]) -> List[int]:
        assert self.teacher_ppl_tokenizer is not None
        token_ids: List[int] = []
        for text in clean_corpus_texts:
            encoded = self.teacher_ppl_tokenizer(
                text,
                add_special_tokens=False,
                return_attention_mask=False,
            )
            token_ids.extend(int(token_id) for token_id in encoded["input_ids"])
        return token_ids

    def get_embedding(self, text: Union[str, List[str]]) -> torch.Tensor:
        is_single = isinstance(text, str)
        texts = [text] if is_single else text
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        ).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            emb = outputs.last_hidden_state[:, 0]
        emb = F.normalize(emb, p=2, dim=1)
        return emb[0].unsqueeze(0) if is_single else emb

    def _get_desc_ppl_context(self, desc_text: str) -> Tuple[torch.Tensor, float]:
        cached = self._desc_ppl_cache.get(desc_text)
        if cached is not None:
            return cached

        assert self.teacher_ppl_tokenizer is not None
        assert self.teacher_ppl_model is not None

        desc_ids = self.teacher_ppl_tokenizer(
            desc_text,
            return_tensors="pt",
            add_special_tokens=False,
        ).input_ids.to(self.device)
        if desc_ids.shape[1] < 2:
            raise ValueError("description context is too short for teacher weighted PPL")

        with torch.no_grad():
            logits = self.teacher_ppl_model(desc_ids).logits

        shift_logits = logits[:, :-1, :]
        shift_labels = desc_ids[:, 1:]
        token_nll = F.cross_entropy(
            shift_logits.reshape(-1, shift_logits.size(-1)),
            shift_labels.reshape(-1),
            reduction="none",
        )
        nll_desc = float(token_nll.mean().item())
        cached = (desc_ids, nll_desc)
        self._desc_ppl_cache[desc_text] = cached
        return cached

    def _compute_batch_weighted_ppl_from_trigger_ids(
        self,
        desc_text: str,
        trigger_id_batches: Sequence[Sequence[int]],
    ) -> List[float]:
        if not trigger_id_batches:
            return []

        assert self.teacher_ppl_model is not None

        desc_ids, nll_desc = self._get_desc_ppl_context(desc_text)
        desc_ids = desc_ids.squeeze(0)
        desc_len = int(desc_ids.shape[0])

        max_trigger_len = max(len(trigger_ids) for trigger_ids in trigger_id_batches)
        if max_trigger_len <= 0:
            return [float(torch.exp(torch.tensor(nll_desc / 2.0)).item())] * len(trigger_id_batches)

        pad_id = int(self.teacher_ppl_tokenizer.pad_token_id)  # type: ignore[arg-type]
        batch_size = len(trigger_id_batches)
        trigger_tensor = torch.full(
            (batch_size, max_trigger_len),
            pad_id,
            dtype=torch.long,
            device=self.device,
        )
        trigger_attention = torch.zeros(
            (batch_size, max_trigger_len),
            dtype=torch.long,
            device=self.device,
        )

        for row_index, trigger_ids in enumerate(trigger_id_batches):
            length = len(trigger_ids)
            if length == 0:
                continue
            trigger_tensor[row_index, :length] = torch.tensor(
                trigger_ids,
                dtype=torch.long,
                device=self.device,
            )
            trigger_attention[row_index, :length] = 1

        desc_batch = desc_ids.unsqueeze(0).expand(batch_size, -1)
        desc_attention = torch.ones_like(desc_batch, dtype=torch.long)
        full_ids = torch.cat([desc_batch, trigger_tensor], dim=1)
        full_attention = torch.cat([desc_attention, trigger_attention], dim=1)

        with torch.no_grad():
            logits = self.teacher_ppl_model(
                full_ids,
                attention_mask=full_attention,
            ).logits

        shift_logits = logits[:, :-1, :]
        shift_labels = full_ids[:, 1:]
        token_nll = F.cross_entropy(
            shift_logits.reshape(-1, shift_logits.size(-1)),
            shift_labels.reshape(-1),
            reduction="none",
        ).view(batch_size, -1)

        trigger_start = desc_len - 1
        trigger_token_nll = token_nll[:, trigger_start:]
        trigger_valid_mask = full_attention[:, desc_len:].float()
        trigger_denominator = trigger_valid_mask.sum(dim=1).clamp(min=1.0)
        nll_trigger = (trigger_token_nll * trigger_valid_mask).sum(dim=1) / trigger_denominator
        ppl_values = torch.exp((nll_trigger + nll_desc) / 2.0)
        return [float(value.item()) for value in ppl_values]

    def _compute_batch_weighted_ppl(
        self,
        desc_text: str,
        trigger_texts: Sequence[str],
    ) -> List[float]:
        assert self.teacher_ppl_tokenizer is not None

        trigger_id_batches: List[List[int]] = []
        for trigger_text in trigger_texts:
            prefixed = " " + trigger_text.strip() if trigger_text.strip() else ""
            encoded = self.teacher_ppl_tokenizer(
                prefixed,
                add_special_tokens=False,
                return_attention_mask=False,
            )
            trigger_id_batches.append([int(token_id) for token_id in encoded["input_ids"]])
        return self._compute_batch_weighted_ppl_from_trigger_ids(desc_text, trigger_id_batches)

    def _sample_natural_trigger_ids(self) -> List[int]:
        pool = self.teacher_natural_token_ids
        if len(pool) >= self.trigger_length:
            return random.sample(pool, self.trigger_length)
        return random.choices(pool, k=self.trigger_length)

    def _calibrate_teacher_tau(self, clean_corpus_texts: Sequence[str]) -> float:
        ppl_values: List[float] = []
        for desc_text in clean_corpus_texts:
            sampled_batches = [
                self._sample_natural_trigger_ids()
                for _ in range(self.teacher_n_samples_per_desc)
            ]
            ppl_values.extend(
                self._compute_batch_weighted_ppl_from_trigger_ids(desc_text, sampled_batches)
            )

        if not ppl_values:
            raise ValueError("teacher_weighted_ppl tau calibration produced no samples")

        values = torch.tensor(ppl_values, dtype=torch.float32)
        quantile = self.teacher_tau_percentile / 100.0
        tau = float(torch.quantile(values, quantile).item())
        return tau

    def _evaluate_teacher_objective_batch(
        self,
        desc_text: str,
        trigger_texts: Sequence[str],
        target_emb: torch.Tensor,
        text_post_trigger: str,
    ) -> List[Dict[str, float]]:
        full_texts = [f"{desc_text} {trigger_text}{text_post_trigger}".strip() for trigger_text in trigger_texts]
        with torch.no_grad():
            batch_emb = self.get_embedding(full_texts)
            sims = F.cosine_similarity(
                batch_emb.unsqueeze(1), target_emb.unsqueeze(0), dim=2
            ).mean(dim=1)
        ppl_values = self._compute_batch_weighted_ppl(desc_text, trigger_texts)
        results: List[Dict[str, float]] = []
        for sim_value, ppl_value in zip(sims.tolist(), ppl_values):
            penalty = max(0.0, ppl_value - float(self.teacher_tau))
            utility = float(sim_value) - self.teacher_ppl_lambda * penalty
            results.append(
                {
                    "similarity": float(sim_value),
                    "ppl_weighted": float(ppl_value),
                    "penalty": float(penalty),
                    "utility": float(utility),
                }
            )
        return results

    def _find_adversarial_trigger_original(
        self,
        text_pre_trigger: str,
        text_post_trigger: str,
        target_texts: List[str],
        patience: int = 3,
    ) -> Tuple[str, List[float]]:
        target_emb = self.get_embedding(target_texts).detach()
        vocab_size = self.tokenizer.vocab_size

        if self.words_only:
            allowed_ids = self._get_allowed_ids()
            trigger_ids = [random.choice(allowed_ids) for _ in range(self.trigger_length)]
        else:
            trigger_ids = [random.randint(0, vocab_size - 1) for _ in range(self.trigger_length)]

        pre_ids = self.tokenizer.encode(text_pre_trigger, add_special_tokens=False)
        post_ids = self.tokenizer.encode(text_post_trigger, add_special_tokens=False)
        trigger_start = len(pre_ids)

        best_loss_so_far = float("inf")
        no_improve = 0
        history: List[float] = []

        for i in trange(self.iterations, desc="Optimizing trigger", leave=False):
            input_ids = pre_ids + trigger_ids + post_ids
            input_tensor = torch.tensor(input_ids, device=self.device).unsqueeze(0)
            input_embeds = self.embeddings[input_tensor].clone()
            input_embeds.requires_grad_()

            outputs = self.model(inputs_embeds=input_embeds)
            current_emb = F.normalize(outputs.last_hidden_state[:, 0], p=2, dim=1)
            sim = F.cosine_similarity(current_emb, target_emb)
            loss = 1 - sim.mean()
            loss.backward()

            trigger_grad = input_embeds.grad[0, trigger_start : trigger_start + self.trigger_length]
            scores = -trigger_grad @ self.embeddings.T
            if self.words_only:
                mask_row = self.word_token_mask.unsqueeze(0).expand(self.trigger_length, -1)
                scores = scores.masked_fill(~mask_row, -float("inf"))

            _, top_k_indices = torch.topk(scores, min(self.top_k, scores.size(1)), dim=1)

            candidate_seq_ids = []
            candidate_positions = []
            for pos in range(self.trigger_length):
                for token_id in top_k_indices[pos]:
                    tmp = trigger_ids[:]
                    tmp[pos] = int(token_id.item())
                    candidate_seq_ids.append(pre_ids + tmp + post_ids)
                    candidate_positions.append((pos, int(token_id.item())))

            best_loss = float("inf")
            best_pos = -1
            best_token = -1

            for start in range(0, len(candidate_seq_ids), self.batch_size):
                end = min(start + self.batch_size, len(candidate_seq_ids))
                batch_ids = candidate_seq_ids[start:end]
                batch_texts = [self.tokenizer.decode(ids, skip_special_tokens=True) for ids in batch_ids]
                with torch.no_grad():
                    batch_emb = self.get_embedding(batch_texts)
                    sim_matrix = F.cosine_similarity(
                        batch_emb.unsqueeze(1), target_emb.unsqueeze(0), dim=2
                    )
                    eval_losses = 1 - sim_matrix.mean(dim=1)
                min_loss, min_idx = torch.min(eval_losses, dim=0)
                if min_loss.item() < best_loss:
                    best_loss = min_loss.item()
                    global_idx = start + int(min_idx.item())
                    best_pos, best_token = candidate_positions[global_idx]

            if best_pos != -1:
                trigger_ids[best_pos] = best_token

            history.append(best_loss)
            if best_loss + 1e-6 < best_loss_so_far:
                best_loss_so_far = best_loss
                no_improve = 0
            else:
                no_improve += 1
                if no_improve >= patience:
                    print(f"[Early stop] no improvement in {patience} iterations at step {i + 1}")
                    break

        trigger_text = self.tokenizer.decode(trigger_ids, skip_special_tokens=True).strip()
        return trigger_text, history

    def _find_adversarial_trigger_teacher_weighted_ppl(
        self,
        text_pre_trigger: str,
        text_post_trigger: str,
        target_texts: List[str],
        patience: int = 3,
    ) -> Tuple[str, List[float]]:
        target_emb = self.get_embedding(target_texts).detach()
        vocab_size = self.tokenizer.vocab_size

        if self.words_only:
            allowed_ids = self._get_allowed_ids()
            trigger_ids = [random.choice(allowed_ids) for _ in range(self.trigger_length)]
        else:
            trigger_ids = [random.randint(0, vocab_size - 1) for _ in range(self.trigger_length)]

        pre_ids = self.tokenizer.encode(text_pre_trigger, add_special_tokens=False)
        post_ids = self.tokenizer.encode(text_post_trigger, add_special_tokens=False)
        trigger_start = len(pre_ids)

        best_utility_so_far = float("-inf")
        no_improve = 0
        history: List[float] = []

        for i in trange(self.iterations, desc="Optimizing trigger", leave=False):
            input_ids = pre_ids + trigger_ids + post_ids
            input_tensor = torch.tensor(input_ids, device=self.device).unsqueeze(0)
            input_embeds = self.embeddings[input_tensor].clone()
            input_embeds.requires_grad_()

            outputs = self.model(inputs_embeds=input_embeds)
            current_emb = F.normalize(outputs.last_hidden_state[:, 0], p=2, dim=1)
            sim = F.cosine_similarity(current_emb, target_emb)
            loss = 1 - sim.mean()
            loss.backward()

            trigger_grad = input_embeds.grad[0, trigger_start : trigger_start + self.trigger_length]
            scores = -trigger_grad @ self.embeddings.T
            if self.words_only:
                mask_row = self.word_token_mask.unsqueeze(0).expand(self.trigger_length, -1)
                scores = scores.masked_fill(~mask_row, -float("inf"))

            _, top_k_indices = torch.topk(scores, min(self.top_k, scores.size(1)), dim=1)

            candidate_trigger_ids: List[List[int]] = [trigger_ids[:]]
            candidate_positions: List[Tuple[int, int]] = [(-1, -1)]
            for pos in range(self.trigger_length):
                for token_id in top_k_indices[pos]:
                    tmp = trigger_ids[:]
                    tmp[pos] = int(token_id.item())
                    candidate_trigger_ids.append(tmp)
                    candidate_positions.append((pos, int(token_id.item())))

            candidate_trigger_texts = [
                self.tokenizer.decode(ids, skip_special_tokens=True).strip()
                for ids in candidate_trigger_ids
            ]

            best_utility = float("-inf")
            best_similarity = float("-inf")
            best_ppl_weighted = float("inf")
            best_pos = -1
            best_token = -1

            for start in range(0, len(candidate_trigger_texts), self.batch_size):
                end = min(start + self.batch_size, len(candidate_trigger_texts))
                batch_trigger_texts = candidate_trigger_texts[start:end]
                batch_scores = self._evaluate_teacher_objective_batch(
                    desc_text=text_pre_trigger,
                    trigger_texts=batch_trigger_texts,
                    target_emb=target_emb,
                    text_post_trigger=text_post_trigger,
                )
                for offset, score_row in enumerate(batch_scores):
                    if score_row["utility"] > best_utility:
                        candidate_index = start + offset
                        best_utility = score_row["utility"]
                        best_similarity = score_row["similarity"]
                        best_ppl_weighted = score_row["ppl_weighted"]
                        best_pos, best_token = candidate_positions[candidate_index]

            if best_pos != -1:
                trigger_ids[best_pos] = best_token

            history.append(best_utility)
            print(
                "[teacher_weighted_ppl] "
                f"iter={i + 1}/{self.iterations} utility={best_utility:.6f} "
                f"sim={best_similarity:.6f} ppl_w={best_ppl_weighted:.6f}"
            )

            if best_utility > best_utility_so_far + 1e-6:
                best_utility_so_far = best_utility
                no_improve = 0
            else:
                no_improve += 1
                if no_improve >= patience:
                    print(f"[Early stop] no improvement in {patience} iterations at step {i + 1}")
                    break

        trigger_text = self.tokenizer.decode(trigger_ids, skip_special_tokens=True).strip()
        return trigger_text, history

    def find_adversarial_trigger(
        self,
        text_pre_trigger: str,
        text_post_trigger: str,
        target_texts: List[str],
        patience: int = 3,
    ) -> Tuple[str, List[float]]:
        if self.attack_mode == "teacher_weighted_ppl":
            return self._find_adversarial_trigger_teacher_weighted_ppl(
                text_pre_trigger=text_pre_trigger,
                text_post_trigger=text_post_trigger,
                target_texts=target_texts,
                patience=patience,
            )
        return self._find_adversarial_trigger_original(
            text_pre_trigger=text_pre_trigger,
            text_post_trigger=text_post_trigger,
            target_texts=target_texts,
            patience=patience,
        )

    def run_attack_with_restarts(
        self,
        text_pre_trigger: str,
        text_post_trigger: str,
        target_texts: List[str],
    ) -> Tuple[str, float, List[float]]:
        best_trigger = ""
        best_sim = -1.0
        best_history: List[float] = []
        best_utility = float("-inf")
        target_emb = self.get_embedding(target_texts)
        self.last_run_metadata = {}

        for i in range(self.restarts):
            print(f"Restart {i + 1}/{self.restarts}")
            trigger, history = self.find_adversarial_trigger(
                text_pre_trigger=text_pre_trigger,
                text_post_trigger=text_post_trigger,
                target_texts=target_texts,
            )
            text_adv = f"{text_pre_trigger} {trigger} {text_post_trigger}".strip()
            adv_emb = self.get_embedding(text_adv)
            sim = F.cosine_similarity(adv_emb, target_emb).mean().item()

            if self.attack_mode == "teacher_weighted_ppl":
                score_row = self._evaluate_teacher_objective_batch(
                    desc_text=text_pre_trigger,
                    trigger_texts=[trigger],
                    target_emb=target_emb,
                    text_post_trigger=text_post_trigger,
                )[0]
                utility = score_row["utility"]
                if utility > best_utility:
                    best_utility = utility
                    best_sim = sim
                    best_trigger = trigger
                    best_history = history
                    self.last_run_metadata = {
                        "attack_mode": self.attack_mode,
                        "teacher_ppl_model": self.teacher_ppl_model_name,
                        "teacher_ppl_lambda": self.teacher_ppl_lambda,
                        "teacher_tau": self.teacher_tau,
                        "teacher_similarity": score_row["similarity"],
                        "teacher_weighted_ppl": score_row["ppl_weighted"],
                        "teacher_penalty": score_row["penalty"],
                        "teacher_utility": score_row["utility"],
                    }
                    print(
                        "New best trigger, "
                        f"utility={best_utility:.4f}, sim={score_row['similarity']:.4f}, "
                        f"ppl_w={score_row['ppl_weighted']:.4f}"
                    )
            else:
                if sim > best_sim:
                    best_sim = sim
                    best_trigger = trigger
                    best_history = history
                    self.last_run_metadata = {
                        "attack_mode": self.attack_mode,
                        "teacher_ppl_model": None,
                        "teacher_ppl_lambda": None,
                        "teacher_tau": None,
                        "teacher_similarity": None,
                        "teacher_weighted_ppl": None,
                        "teacher_penalty": None,
                        "teacher_utility": None,
                    }
                    print(f"New best trigger, avg train similarity: {best_sim:.4f}")

        return best_trigger, best_sim, best_history
