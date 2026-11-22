"""Stage 3 (GPU, one reader per process): answer every query under every setup [design_spec 4.1, 7].

Request id = item|store|query|qv|setup. Outputs are cached in generations_<model>.jsonl; reruns only
fill in missing ids, so a crashed Kaggle session can simply be restarted.
"""
import json

from . import config, haystack, prompts


def memory_text(unit_text, strategy, store, en):
    """How a stored memory is shown to the reader under each strategy. English memories need no translation."""
    if store == "en" or strategy == "S1":
        return unit_text
    if strategy == "S2":
        return en.get(unit_text, unit_text)
    return f"{unit_text} (English: {en.get(unit_text, unit_text)})"   # S3


def build_requests(items, setups=config.SETUPS):
    hist = {(h["item_id"], h["lang"]): h for h in haystack.load_jsonl(config.RESULTS / "histories.jsonl")}
    ret = {}
    if any(s.startswith("RM") for s in setups):
        ret = {(r["item_id"], r["store"], r["query"], r["qv"], r["strategy"]): r["ranked"]
               for r in haystack.load_jsonl(config.RESULTS / "retrieval.jsonl") if r["retriever"] == "bge-m3"}
    en = json.loads(config.TRANSLATION_CACHE.read_text(encoding="utf-8"))
    reqs = []
    for it in items:
        for s in config.STORE_LANGS:
            h = hist[(it["item_id"], s)]
            unit_text = dict(haystack.units(h))
            order = [u for u, _ in haystack.units(h)]
            for q in config.LANGS:
                for qv in config.QUERY_VARIANTS:
                    query = it["text"][q][qv]
                    for setup in setups:
                        rid = f"{it['item_id']}|{s}|{q}|{qv}|{setup}"
                        if setup == "FC":
                            sessions = [[{"role": t["role"], "content": t["content"]} for t in sess]
                                        for sess in h["sessions"]]
                            msgs = prompts.reader_fc(sessions, query)
                        else:
                            kind, strat = setup.split("-")
                            if kind == "RM":
                                chosen = ret[(it["item_id"], s, q, qv, strat)][:config.TOP_K]
                            else:  # oracle: gold (+ distractor) in chronological order
                                chosen = sorted([u for u in (h["gold_unit"], h["distractor_unit"]) if u],
                                                key=order.index)
                            mems = [memory_text(unit_text[u], strat, s, en) for u in chosen]
                            msgs = prompts.reader_memories(mems, query)
                        reqs.append({"id": rid, "messages": msgs})
    # Full-context prompts that share a history go first and back to back, so vLLM's prefix cache can reuse the
    # (up to ~23k-token) history across the 3 query languages x query variants. Python's sort is stable.
    reqs.sort(key=lambda r: r["id"].split("|")[4] != "FC")
    return reqs


def run(items_path, model_key, backend=None, setups=config.SETUPS):
    from .llm import Generator
    items = haystack.load_items(items_path)
    reqs = build_requests(items, setups)
    out_path = config.RESULTS / f"generations_{model_key}.jsonl"
    done = {r["id"] for r in haystack.load_jsonl(out_path)} if out_path.exists() else set()
    todo = [r for r in reqs if r["id"] not in done]
    print(f"{model_key}: {len(reqs)} requests, {len(todo)} to run")
    if not todo:
        return
    gen = Generator(model_key, backend=backend)
    chunk = 2000   # write to disk regularly so a crash loses little
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]
        outs = gen.chat([r["messages"] for r in part], max_tokens=config.READER_MAX_TOKENS)
        with open(out_path, "a", encoding="utf-8") as f:
            for r, o in zip(part, outs):
                f.write(json.dumps({"id": r["id"], "model": model_key, "response": o}, ensure_ascii=False) + "\n")
        print(f"  wrote {i + len(part)}/{len(todo)}")
