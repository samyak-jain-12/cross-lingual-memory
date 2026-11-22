"""Stage 4 (GPU): LLM judge over every generation [design_spec 6.2]. Cached in judgments.jsonl."""
import json
import re

from . import config, haystack, prompts

LABEL = re.compile(r"\b(CORRECT|INCORRECT|NO_ANSWER|ANSWERED)\b")


def parse(text):
    m = LABEL.search(text.upper())
    return m.group(1) if m else "UNPARSED"


def run(items_path, backend=None):
    from .llm import Generator
    items = {i["item_id"]: i for i in haystack.load_jsonl(items_path)}
    gens = []
    for p in sorted(config.RESULTS.glob("generations_*.jsonl")):
        gens += haystack.load_jsonl(p)
    out_path = config.RESULTS / "judgments.jsonl"
    done = {(r["id"], r["model"]) for r in haystack.load_jsonl(out_path)} if out_path.exists() else set()
    todo = [g for g in gens if (g["id"], g["model"]) not in done]
    print(f"judge: {len(gens)} generations, {len(todo)} to judge")
    if not todo:
        return
    msgs = []
    for g in todo:
        iid, s, q, qv, setup = g["id"].split("|")
        it = items[iid]
        query = it["text"][q][qv]
        if it.get("is_answerable", True):
            aliases = [a for sl in it["gold"]["slots"] for a in sl["aliases"]]
            msgs.append(prompts.judge(query, it["gold"]["answer_en"], aliases, g["response"]))
        else:
            msgs.append(prompts.judge_abstention(query, g["response"]))
    gen = Generator("judge", backend=backend)
    outs = gen.chat(msgs, max_tokens=8)
    with open(out_path, "a", encoding="utf-8") as f:
        for g, o in zip(todo, outs):
            f.write(json.dumps({"id": g["id"], "model": g["model"], "judge_raw": o, "judge": parse(o)},
                               ensure_ascii=False) + "\n")
