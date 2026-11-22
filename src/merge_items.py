"""Endsem: merge all built batches into the single item file for the main run (ENDSEM_PLAN.md §3, change 6).

Reads  data/items/items_<batch>.jsonl for every batch in BATCHES
Writes data/items/items_main.jsonl  (165 items: 150 answerable + 15 controls)

What changes compared with the per-batch files:
  - evidence_class (early / middle / late) is re-balanced over the whole set, within each memory type, and
    crossed with has_distractor so distractor items are spread over positions too. haystack.py maps the class
    to a session slot for any history length, so the Short (10) and Long (20) histories put the same item at
    the same relative position. The old per-batch evidence_position is kept only for reference.
  - every item gets an ablation block membership:
      abl_short  : 20 answerable items per type (Short-history ablation, ENDSEM_PLAN §1 block A)
      abl_q3     : items that have a q3 (block B, 17 per type)
      abl_digits : all 50 events (block C)
  - banned_fillers: filler sessions this item's history must not use (spec §3.5 "drop any filler that mentions
    the slot value"): every filler whose EN/HI/HG text contains one of the item's gold aliases, plus fillers
    that would answer the item's control question (CONTROL_TRAPS). Controls reuse their base item's list.
Run from the project root:  python src/merge_items.py
"""
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from build_items import date_aliases          # noqa: E402
from clm.textutil import contains_exact as contains   # noqa: E402  (strict: frozen data must not change)

# Fillers that would give a real answer to a control question (checked by hand against the 40 EN fillers, 19 Nov).
CONTROL_TRAPS = {"E046": r"\byoga\b", "P019": r"\byoga\b"}
BATCHES = ["batch01_pilot", "batch02", "batch03", "batch04", "batch05", "batch06_controls"]
CLASSES = ("early", "middle", "late")
N_SHORT = 20


def load(batch):
    with open(ROOT / f"data/items/items_{batch}.jsonl", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    items = [it for b in BATCHES for it in load(b)]
    ids = [i["item_id"] for i in items]
    dup = [k for k, n in Counter(ids).items() if n > 1]
    if dup:
        sys.exit(f"duplicate item ids: {dup}")
    by_id = {i["item_id"]: i for i in items}
    ans = [i for i in items if i.get("is_answerable", True)]
    ctrl = [i for i in items if not i.get("is_answerable", True)]
    missing = [c["item_id"] for c in ctrl if c["base_item"] not in by_id]
    if missing:
        sys.exit(f"controls with missing base items: {missing}")

    for mtype in ("fact", "preference", "event"):
        pool = sorted((i for i in ans if i["memory_type"] == mtype), key=lambda i: i["item_id"])
        rng = random.Random(f"merge-{mtype}")
        # Balanced position classes, assigned separately within distractor / no-distractor items.
        k = 0
        for dis in (True, False):
            grp = [i for i in pool if bool(i.get("has_distractor")) == dis]
            rng.shuffle(grp)
            for i in grp:
                i["evidence_class"] = CLASSES[k % 3]
                k += 1
        # Short-history ablation subset: 20 per type, stratified over position classes.
        chosen = []
        for c in CLASSES:
            grp = sorted((i for i in pool if i["evidence_class"] == c), key=lambda i: i["item_id"])
            rng.shuffle(grp)
            chosen += grp[: round(N_SHORT * len(grp) / len(pool))]
        for i in pool:
            i["abl_short"] = i in chosen
            i["abl_q3"] = all("q3" in i["text"][l] for l in ("en", "hi", "hg"))
            i["abl_digits"] = mtype == "event"

    # Banned fillers (any language version mentioning the gold value, or answering the control question).
    pools = {}
    for lang in ("en", "hi", "hg"):
        with open(ROOT / f"data/haystacks/filler_pool_{lang}.jsonl", encoding="utf-8") as f:
            for s in (json.loads(l) for l in f if l.strip()):
                pools.setdefault(s["filler_id"], []).extend(t["content"] for t in s["turns"])
    ftext = {fid: " ".join(ts) for fid, ts in pools.items()}
    en_text = {}
    with open(ROOT / "data/haystacks/filler_pool_en.jsonl", encoding="utf-8") as f:
        for s in (json.loads(l) for l in f if l.strip()):
            en_text[s["filler_id"]] = " ".join(t["content"] for t in s["turns"])
    for i in ans:
        g = i["gold"]
        aliases = date_aliases(g["date"]["day"], g["date"]["month"]) if "date" in g else \
            [a for s in g["slots"] for a in s["aliases"]]
        banned = {fid for fid, t in ftext.items() if any(contains(t, a) for a in aliases)}
        if i["item_id"] in CONTROL_TRAPS:
            banned |= {fid for fid, t in en_text.items() if re.search(CONTROL_TRAPS[i["item_id"]], t, re.I)}
        i["banned_fillers"] = sorted(banned)
        if len(ftext) - len(banned) < 19:
            sys.exit(f"{i['item_id']}: only {len(ftext) - len(banned)} usable fillers, need 19")

    for c in ctrl:   # controls share their base item's history; they are only in the main block
        c["evidence_class"] = by_id[c["base_item"]]["evidence_class"]
        c["banned_fillers"] = by_id[c["base_item"]]["banned_fillers"]
        c["abl_short"] = c["abl_q3"] = c["abl_digits"] = False

    out = ROOT / "data/items/items_main.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    print(f"wrote {out.relative_to(ROOT)}: {len(ans)} answerable + {len(ctrl)} controls")
    print("type x position:", dict(sorted(Counter((i["memory_type"], i["evidence_class"]) for i in ans).items())))
    print("distractor x position:", dict(sorted(Counter(i["evidence_class"] for i in ans if i.get("has_distractor")).items())))
    print("abl_short per type:", dict(Counter(i["memory_type"] for i in ans if i["abl_short"])))
    print("abl_q3 per type:", dict(Counter(i["memory_type"] for i in ans if i["abl_q3"])))
    print("abl_digits:", sum(i["abl_digits"] for i in ans))
    print("items with banned fillers:", {i["item_id"]: len(i["banned_fillers"]) for i in ans if i["banned_fillers"]})


if __name__ == "__main__":
    main()
