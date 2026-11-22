"""Phase 3, step 5: build the 40-session English filler pool (design_spec.md §3.5).

Filler sessions come from LongMemEval-S haystacks, excluding any evidence session. Each is trimmed
to 2 user + 2 assistant turns, with assistant turns cut to <= 80 words at a sentence boundary.
Sessions that mention any gold or distractor value of our items are dropped, so filler can never
answer (or mislead) a query. HI/HG versions are produced later by the fixed translator (Phase 4).

Writes data/haystacks/filler_pool_en.jsonl
Run from the project root:  python src/build_filler_pool.py
"""
import json
import random
import re
from pathlib import Path

from build_items import contains

ROOT = Path(__file__).resolve().parents[1]
N_POOL = 40
SEED = 20261003
MAX_ASSIST_WORDS = 80
SENT = re.compile(r"(?<=[.!?])\s+")


def trim(text, max_words):
    text = re.sub(r"[*#`>|]", "", text)            # strip markdown
    text = re.sub(r"\s+", " ", text).strip()
    out, n = [], 0
    for s in SENT.split(text):
        w = len(s.split())
        if n + w > max_words:
            break
        out.append(s)
        n += w
    return " ".join(out) if out else " ".join(text.split()[:max_words])


def item_values():
    vals = []
    for p in (ROOT / "data/items").glob("items_*.jsonl"):
        for line in p.open(encoding="utf-8"):
            it = json.loads(line)
            for s in it.get("gold", {}).get("slots", []):
                vals += s["aliases"]
            vals += it.get("distractor", {}).get("value_aliases", [])
            vals += it.get("near_miss_aliases", [])
    # Short numeric/date strings are too generic to filter on alone; keep multi-character names.
    return [v for v in set(vals) if len(v) >= 4 and not re.fullmatch(r"[\d:.\s-]+", v)]


def main():
    data = json.loads((ROOT / "data/raw/longmemeval_s_cleaned.json").read_text())
    banned = item_values()
    seen, pool = set(), []
    for x in data:
        for sid, sess in zip(x["haystack_session_ids"], x["haystack_sessions"]):
            if sid in seen or any(t.get("has_answer") for t in sess) or "answer" in sid:
                continue
            seen.add(sid)
            turns = [t for t in sess if t["role"] in ("user", "assistant")][:4]
            if [t["role"] for t in turns] != ["user", "assistant", "user", "assistant"]:
                continue
            u1, u2 = (len(turns[i]["content"].split()) for i in (0, 2))
            if not (8 <= u1 <= 70 and 4 <= u2 <= 70):
                continue
            sess_out = [{"role": t["role"],
                         "content": trim(t["content"], 70 if t["role"] == "user" else MAX_ASSIST_WORDS)}
                        for t in turns]
            blob = " ".join(t["content"] for t in sess_out)
            if any(contains(blob, v) for v in banned):
                continue
            pool.append({"session_id": sid, "turns": sess_out})

    random.Random(SEED).shuffle(pool)
    chosen = pool[:N_POOL]
    out = ROOT / "data/haystacks/filler_pool_en.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for i, s in enumerate(chosen, 1):
            f.write(json.dumps({"filler_id": f"FL{i:02d}", **s}, ensure_ascii=False) + "\n")
    words = [sum(len(t["content"].split()) for t in s["turns"]) for s in chosen]
    print(f"eligible sessions: {len(pool)} | wrote {len(chosen)} -> {out.relative_to(ROOT)}")
    print(f"words per filler session: min {min(words)}, mean {sum(words)/len(words):.0f}, max {max(words)}")


if __name__ == "__main__":
    main()
