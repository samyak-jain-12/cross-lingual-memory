"""Token counts of full-context prompts per storage language and tokenizer [design_spec 3.5 CHECK IN PHASE 4].

Hindi/Hinglish need more tokens than English for the same content; we report this and confirm every
prompt fits MAX_MODEL_LEN. Writes table_tokens.csv.
"""
import csv

from . import config, generate, haystack


def run(items_path):
    from transformers import AutoTokenizer
    items = haystack.load_items(items_path)
    reqs = [r for r in generate.build_requests(items, setups=("FC",)) if r["id"].split("|")[3] == config.QUERY_VARIANTS[0]]
    rows = []
    for key in ("qwen3-8b", "llama3.1-8b"):
        tok = AutoTokenizer.from_pretrained(config.MODELS[key])
        by_lang = {}
        for r in reqs:
            # Render to text, then tokenize: in transformers 5.x apply_chat_template(tokenize=True) returns a
            # dict, and len() of it was 2 in the first pilot. The template already holds special tokens.
            text = tok.apply_chat_template(r["messages"], tokenize=False, add_generation_prompt=True)
            n = len(tok(text, add_special_tokens=False)["input_ids"])
            by_lang.setdefault(r["id"].split("|")[1], []).append(n)
        for lang, ns in sorted(by_lang.items()):
            rows.append({"tokenizer": key, "store_lang": lang, "prompts": len(ns), "mean_tokens": round(sum(ns) / len(ns)),
                         "max_tokens": max(ns), "fits_context": max(ns) + config.READER_MAX_TOKENS <= config.MAX_MODEL_LEN})
    with open(config.RESULTS / "table_tokens.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)
    if not all(r["fits_context"] for r in rows):
        raise RuntimeError("Some full-context prompts exceed MAX_MODEL_LEN - see table_tokens.csv")
