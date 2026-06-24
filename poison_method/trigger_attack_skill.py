"""
Adversarial trigger optimizer for skill description poisoning experiments.
"""

import os
import random
from typing import List, Tuple, Union

import torch
import torch.nn.functional as F
from tqdm.auto import trange
from transformers import AutoModel, AutoTokenizer


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

        self.tokenizer = AutoTokenizer.from_pretrained(emb_model)
        self.model = AutoModel.from_pretrained(emb_model).to(self.device)
        self.model.eval()
        self.embeddings = self.model.get_input_embeddings().weight
        self.embeddings.requires_grad = False

        self._create_word_token_mask()
        print(f"Loaded embedding model: {emb_model}")

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

    def find_adversarial_trigger(
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
                    print(f"[Early stop] no improvement in {patience} iterations at step {i+1}")
                    break

        trigger_text = self.tokenizer.decode(trigger_ids, skip_special_tokens=True).strip()
        return trigger_text, history

    def run_attack_with_restarts(
        self,
        text_pre_trigger: str,
        text_post_trigger: str,
        target_texts: List[str],
    ) -> Tuple[str, float, List[float]]:
        best_trigger = ""
        best_sim = -1.0
        best_history: List[float] = []
        target_emb = self.get_embedding(target_texts)

        for i in range(self.restarts):
            print(f"Restart {i+1}/{self.restarts}")
            trigger, history = self.find_adversarial_trigger(
                text_pre_trigger=text_pre_trigger,
                text_post_trigger=text_post_trigger,
                target_texts=target_texts,
            )
            text_adv = f"{text_pre_trigger} {trigger} {text_post_trigger}".strip()
            adv_emb = self.get_embedding(text_adv)
            sim = F.cosine_similarity(adv_emb, target_emb).mean().item()
            if sim > best_sim:
                best_sim = sim
                best_trigger = trigger
                best_history = history
                print(f"New best trigger, avg train similarity: {best_sim:.4f}")

        return best_trigger, best_sim, best_history
