"""Chat-generation wrapper: vLLM (default), Hugging Face transformers (fallback), or a mock (local tests).

All backends use greedy decoding (temperature 0) and fp16 [design_spec 5.1]. Qwen3 thinking mode is
disabled through the chat template [5.1].
"""
import os
import re

from . import config

THINK = re.compile(r"<think>.*?</think>", re.S)


def _clean(text):
    return THINK.sub("", text).strip()


class Generator:
    def __init__(self, model_key, backend=None, max_model_len=None):
        self.model_key = model_key
        self.model_id = config.MODELS[model_key]
        self.backend = backend or os.environ.get("CLM_BACKEND", "vllm")
        self.max_model_len = max_model_len or config.MODEL_LEN.get(model_key, config.MAX_MODEL_LEN)
        if self.backend == "vllm":
            self._init_vllm()
        elif self.backend == "hf":
            self._init_hf()
        elif self.backend != "mock":
            raise ValueError(f"unknown backend {self.backend}")

    # ---------------- vLLM ----------------
    def _init_vllm(self):
        import torch
        from vllm import LLM
        self.llm = LLM(model=self.model_id, dtype="half", tensor_parallel_size=max(1, torch.cuda.device_count()),
                       max_model_len=self.max_model_len, gpu_memory_utilization=0.88,
                       enable_prefix_caching=True, seed=0)

    def _gen_vllm(self, conversations, max_tokens):
        from vllm import SamplingParams
        sp = SamplingParams(temperature=0.0, max_tokens=max_tokens)
        outs = self.llm.chat(conversations, sp, use_tqdm=True,
                             chat_template_kwargs={"enable_thinking": False})
        return [_clean(o.outputs[0].text) for o in outs]

    # ---------------- transformers ----------------
    def _init_hf(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(self.model_id, padding_side="left")
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id, torch_dtype=torch.float16, device_map="auto")
        self.model.eval()

    def _gen_hf(self, conversations, max_tokens, batch_size=4):
        import torch
        out = []
        for i in range(0, len(conversations), batch_size):
            batch = conversations[i:i + batch_size]
            texts = [self.tok.apply_chat_template(c, tokenize=False, add_generation_prompt=True,
                                                  enable_thinking=False) for c in batch]
            enc = self.tok(texts, return_tensors="pt", padding=True).to(self.model.device)
            with torch.no_grad():
                gen = self.model.generate(**enc, max_new_tokens=max_tokens, do_sample=False,
                                          pad_token_id=self.tok.pad_token_id)
            for row in gen[:, enc["input_ids"].shape[1]:]:
                out.append(_clean(self.tok.decode(row, skip_special_tokens=True)))
        return out

    # ---------------- mock (CPU tests) ----------------
    def _gen_mock(self, conversations, max_tokens):
        """Echoes the first memory line for readers, copies the text for translators, says CORRECT for judges."""
        out = []
        for c in conversations:
            msg = c[-1]["content"]
            if "Reply with exactly one word" in msg:
                out.append("NO_ANSWER" if "ANSWERED -" in msg else "CORRECT")
            elif msg.startswith(("Translate", "Rewrite", "Write the following")):
                out.append(msg.split("Text:", 1)[-1].strip())
            else:
                m = re.search(r"\n1\. (.+)", msg) or re.search(r"User: (.+)", msg)
                out.append(m.group(1)[:200] if m else "I don't know.")
        return out

    def chat(self, conversations, max_tokens):
        if not conversations:
            return []
        return getattr(self, f"_gen_{self.backend}")(conversations, max_tokens)
