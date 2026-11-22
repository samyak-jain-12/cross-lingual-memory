"""Phase 3, step 1: extract candidate memory items from LongMemEval (design_spec.md §3.1-3.2).

Writes data/candidates/candidates.csv. Automatic filters cover eligibility rules 1-2
(single user-evidence turn, short answer). Rules 3-6 (personal, translatable,
unambiguous, topic balance) need a human pass: the `keep` column is filled by the team.

Run from the project root:  python src/build_candidates.py
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/raw/longmemeval_oracle.json"
OUT = ROOT / "data/candidates/candidates.csv"

MONTHS = ("January|February|March|April|May|June|July|August|September|October|November|December|"
          "Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec")
DATE_RE = re.compile(
    rf"\b(?:(?:{MONTHS})\.?\s+\d{{1,2}}(?:st|nd|rd|th)?|\d{{1,2}}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:{MONTHS}))\b")
SENT_RE = re.compile(r"(?<=[.!?])\s+")

# Coarse topic tags for the "max 5 per topic cluster" rule (§3.2 rule 6). First match wins.
TOPICS = [
    ("vehicles", r"\b(car|bike|vehicle|tire|tyre|gps|mechanic|service[d]?)\b"),
    ("pets", r"\b(dog|cat|puppy|kitten|pet|retriever|vet)\b"),
    ("food/cooking", r"\b(recipe|cook|bake|cake|rice|restaurant|dinner|coffee|gin|cocktail|food)\b"),
    ("fitness/health", r"\b(gym|yoga|run|5k|marathon|workout|doctor|bronchitis|fitness|health)\b"),
    ("travel", r"\b(trip|flight|travel|hotel|vacation|hawaii|visit(ed)?)\b"),
    ("work/study", r"\b(job|work|office|degree|university|college|course|startup|commute|boss)\b"),
    ("media/books/games", r"\b(book|novel|audiobook|podcast|album|playlist|song|movie|show|game|spotify)\b"),
    ("shopping/home", r"\b(bought|buy|store|shop|ikea|target|furniture|paint|bulb|tv|laptop|phone)\b"),
    ("family/social", r"\b(sister|brother|mom|dad|mother|father|friend|wedding|party|family)\b"),
    ("hobbies", r"\b(photograph|camera|garden|painting|guitar|piano|knit|craft|hobby)\b"),
]


def topic_of(text):
    t = text.lower()
    for name, pat in TOPICS:
        if re.search(pat, t):
            return name
    return "other"


def user_evidence(item):
    return [t["content"] for s in item["haystack_sessions"] for t in s
            if t.get("has_answer") and t["role"] == "user"]


def main():
    data = json.loads(SRC.read_text())
    rows = []

    for x in data:
        qtype, qid = x["question_type"], x["question_id"]
        if qid.endswith("_abs"):
            continue
        ev = user_evidence(x)

        # Facts: single-session-user, one evidence turn.
        if qtype == "single-session-user" and len(ev) == 1:
            ans = str(x["answer"])
            flags = []
            if len(ans.split()) > 6:
                flags.append("long_answer")
            rows.append(dict(type="fact", lme_qid=qid, lme_type=qtype, question=x["question"],
                             answer=ans, evidence=ev[0], evidence_sentence="", date_mention="",
                             flags=";".join(flags)))

        # Preferences: rubric answers -> need a rewritten short-answer question.
        elif qtype == "single-session-preference" and ev:
            rows.append(dict(type="preference", lme_qid=qid, lme_type=qtype, question=x["question"],
                             answer=str(x["answer"]), evidence=ev[0], evidence_sentence="",
                             date_mention="",
                             flags="rubric_answer_rewrite" + (";multi_evidence" if len(ev) > 1 else "")))

        # Events: every user evidence turn with an explicit calendar date becomes one candidate.
        if qtype in ("temporal-reasoning", "multi-session", "knowledge-update"):
            for turn in ev:
                m = DATE_RE.search(turn)
                if not m:
                    continue
                sent = next((s for s in SENT_RE.split(turn) if m.group(0) in s), turn)
                rows.append(dict(type="event", lme_qid=qid, lme_type=qtype, question="(write single-hop)",
                                 answer="", evidence=turn, evidence_sentence=sent.strip(),
                                 date_mention=m.group(0), flags="needs_question"))

    # De-duplicate events that share the same dated sentence.
    seen, uniq = set(), []
    for r in rows:
        key = (r["type"], r["evidence_sentence"] or r["evidence"])
        if key not in seen:
            seen.add(key)
            uniq.append(r)

    for i, r in enumerate(uniq, 1):
        r["cand_id"] = f"{r['type'][0].upper()}C{i:03d}"
        r["topic"] = topic_of(r["evidence_sentence"] or r["evidence"])
        r["evidence_words"] = len(r["evidence"].split())
        r["keep"] = ""
        r["notes"] = ""

    cols = ["cand_id", "type", "topic", "lme_qid", "lme_type", "question", "answer", "date_mention",
            "evidence_sentence", "evidence", "evidence_words", "flags", "keep", "notes"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows({c: r[c] for c in cols} for r in uniq)

    from collections import Counter
    print(f"wrote {len(uniq)} candidates -> {OUT.relative_to(ROOT)}")
    print("by type:", dict(Counter(r["type"] for r in uniq)))
    for t in ("fact", "preference", "event"):
        print(f"  {t} topics:", dict(Counter(r["topic"] for r in uniq if r["type"] == t)))


if __name__ == "__main__":
    main()
