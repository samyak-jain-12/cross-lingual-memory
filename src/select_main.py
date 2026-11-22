"""Endsem step 2: fix the 120 new items + 12 new controls for the main study (ENDSEM_PLAN.md §2).

Reads  data/candidates/candidates.csv, data/candidates/pref_extra.csv, data/items/drafts/batch01_pilot.json
Writes data/candidates/selection_main.csv   (one row per new item / control, with all design assignments)

Assignments, stratified within each memory type so every batch is balanced:
  - user_gender: 20 female / 20 male (alternating, so each batch of 10 gets 5/5)
  - has_distractor: 22 of 40 new items, so 25 of 50 including the pilot's 3 per type (spec rule §8: 50%)
  - has_q3 (indirect-question ablation): 17 of 40
  - batch: batch02..batch05, 10 items per type each
Run from the project root:  python src/select_main.py
"""
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCHES = ["batch02", "batch03", "batch04", "batch05"]
N_DISTRACTOR, N_Q3 = 22, 17
PREFIX = {"fact": "F", "preference": "P", "event": "E"}

# 12 new unanswerable controls (4 per type, 5 per type with the pilot's). The queried detail is never
# stated, but a closely related one is (spec §3.3). base = candidate whose history the control reuses.
CONTROLS = [
    ("fact", "FC120", "How long did it take me to assemble my IKEA desk?", "only the bookshelf assembly time is stated"),
    ("fact", "FC137", "Where did I do my Master's degree?", "only the Bachelor's (UCLA) is stated"),
    ("fact", "FC162", "Which city does my brother live in?", "only sister Emily's city is stated"),
    ("fact", "FC134", "How much storage does my laptop have?", "only the RAM (16GB) is stated"),
    ("preference", "PX0070", "Which yoga pose do I like least?", "only the favourite pose is stated"),
    ("preference", "PX0221", "Which cricket team do I support?", "only the football team is stated"),
    ("preference", "PX0137", "What dish do I always order at my favourite restaurant?", "only the restaurant is stated"),
    ("preference", "PX0616", "Which Depeche Mode song is my favourite?", "only the favourite album is stated"),
    ("event", "EC023", "When did I run my first half marathon?", "only the date the running shoes were bought is stated"),
    ("event", "EC055", "When did I buy my road bike?", "only the bike service date is stated"),
    ("event", "EC042", "When did I move into my new townhouse?", "only the offer date is stated"),
    ("event", "EC066", "When did I start going to yoga classes?", "only the mindfulness workshop date is stated"),
]


def spread(n_total, n_true, rng):
    """n_true True values spread evenly over n_total positions (one per stratum of size n_total/n_true), then jittered."""
    flags = [False] * n_total
    step = n_total / n_true
    for k in range(n_true):
        lo, hi = int(k * step), max(int(k * step) + 1, int((k + 1) * step))
        flags[rng.randrange(lo, hi)] = True
    return flags


def main():
    pilot = json.loads((ROOT / "data/items/drafts/batch01_pilot.json").read_text(encoding="utf-8"))
    used = {i["cand_id"] for i in pilot["items"] if i.get("cand_id")}
    with (ROOT / "data/candidates/candidates.csv").open(encoding="utf-8") as f:
        cands = [r for r in csv.DictReader(f) if r["keep"] == "Y" and r["cand_id"] not in used]
    with (ROOT / "data/candidates/pref_extra.csv").open(encoding="utf-8") as f:
        prefx = [r for r in csv.DictReader(f) if r["keep"] == "Y"]

    pools = {
        "fact": [dict(cand_id=r["cand_id"], source="candidates.csv", topic=r["topic"], lme_qid=r["lme_qid"],
                      question=r["question"], answer=r["answer"], evidence=r["evidence_sentence"] or r["evidence"])
                 for r in cands if r["type"] == "fact"],
        "event": [dict(cand_id=r["cand_id"], source="candidates.csv", topic=r["topic"], lme_qid=r["lme_qid"],
                       question="(write single-hop)", answer=r["date_mention"], evidence=r["evidence_sentence"])
                  for r in cands if r["type"] == "event"],
        "preference": [dict(cand_id=r["cand_id"], source="candidates.csv", topic=r["topic"], lme_qid=r["lme_qid"],
                            question=r["notes"].split("->")[0].replace("Q:", "").strip(),
                            answer=r["notes"].split("->")[1].strip() if "->" in r["notes"] else "",
                            evidence="(from LongMemEval preference session)")
                       for r in cands if r["type"] == "preference"]
                      + [dict(cand_id=r["pcand_id"], source="pref_extra.csv", topic="", lme_qid=r["session_id"],
                              question=r["question"], answer=r["answer"], evidence=r["sentence"]) for r in prefx],
    }

    rows = []
    for mtype, pool in pools.items():
        assert len(pool) == 40, f"{mtype}: {len(pool)} candidates, need 40"
        rng = random.Random(f"select-{mtype}")
        dis = spread(40, N_DISTRACTOR, rng)
        q3 = spread(40, N_Q3, rng)
        for k, c in enumerate(pool):
            rows.append({"item_id": f"{PREFIX[mtype]}{11 + k:03d}", "memory_type": mtype,
                         "batch": BATCHES[k // 10], "user_gender": "female" if k % 2 == 0 else "male",
                         "has_distractor": "Y" if dis[k] else "N", "has_q3": "Y" if q3[k] else "N",
                         "is_answerable": "Y", "base_item": "", **c, "control_note": ""})

    by_cand = {r["cand_id"]: r for r in rows}
    n_ctrl = {}
    for mtype, cand, q, note in CONTROLS:
        base = by_cand[cand]
        n_ctrl[mtype] = n_ctrl.get(mtype, 0) + 1
        rows.append({"item_id": f"{base['item_id']}-ABS", "memory_type": mtype, "batch": "batch06_controls",
                     "user_gender": base["user_gender"], "has_distractor": "", "has_q3": "N",
                     "is_answerable": "N", "base_item": base["item_id"], "cand_id": cand, "source": base["source"],
                     "topic": base["topic"], "lme_qid": base["lme_qid"], "question": q,
                     "answer": "NO_ANSWER", "evidence": "", "control_note": note})

    out = ROOT / "data/candidates/selection_main.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Summary.
    from collections import Counter
    ans = [r for r in rows if r["is_answerable"] == "Y"]
    print(f"wrote {out.relative_to(ROOT)}: {len(ans)} items + {len(rows) - len(ans)} controls")
    for key in ("user_gender", "has_distractor", "has_q3"):
        print(key, dict(sorted(Counter((r["memory_type"], r[key]) for r in ans).items())))
    print("per batch", dict(sorted(Counter((r["batch"], r["memory_type"]) for r in rows).items())))
    print("distractor per batch", dict(sorted(Counter(r["batch"] for r in ans if r["has_distractor"] == "Y").items())))


if __name__ == "__main__":
    main()
