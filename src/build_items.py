"""Phase 3, step 3: validate drafted items and build the item file (design_spec.md §3.3-3.5).

Reads  data/items/drafts/<batch>.json
Writes data/items/items_<batch>.jsonl   (expanded: date aliases, positions, seeds, source info)
       data/items/qa_<batch>.txt        (automatic QA report: must be clean before verification)

Run from the project root:  python src/build_items.py batch01_pilot
"""
import csv
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGS = ("en", "hi", "hg")
TURN_FIELDS = ("memory_turn", "assistant_reply", "followup_turn", "followup_reply")
POSITIONS = (2, 5, 9)  # evidence session slot in a 10-session history (spec §3.5)

MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August",
             "September", "October", "November", "December"]
MONTHS_HI = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त",
             "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
MONTHS_HI_ALT = {"फ़रवरी": ["फरवरी"], "सितंबर": ["सितम्बर"], "अक्टूबर": ["अक्तूबर"],
                 "नवंबर": ["नवम्बर"], "दिसंबर": ["दिसम्बर"]}

# First-person verb forms that reveal the speaker's gender (user turns only).
MASC = {"hi": re.compile(r"(रहा|करता|सकता|गया|चुका|चाहता|सोचता|देखता) (हूँ|था)"),
        "hg": re.compile(r"\b(raha|karta|sakta|gaya|chuka|chahta|sochta|dekhta) (hoon|tha)\b", re.I)}
FEM = {"hi": re.compile(r"(रही|करती|सकती|गई|चुकी|चाहती|सोचती|देखती) (हूँ|थी)"),
       "hg": re.compile(r"\b(rahi|karti|sakti|gayi|chuki|chahti|sochti|dekhti) (hoon|thi)\b", re.I)}


def norm(s):
    return unicodedata.normalize("NFC", s).casefold()


def contains(text, alias):
    """Alias match: word-bounded for Latin script, substring for Devanagari."""
    t, a = norm(text), norm(alias)
    if re.search(r"[a-z0-9]", a):
        return re.search(rf"(?<![a-z0-9]){re.escape(a)}(?![a-z0-9])", t) is not None
    return a in t


def date_aliases(day, month):
    en, hi = MONTHS_EN[month - 1], MONTHS_HI[month - 1]
    suf = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    out = [f"{en} {day}", f"{en} {day}{suf}", f"{day} {en}", f"{day}{suf} {en}",
           f"{day}{suf} of {en}", f"{en[:3]} {day}", f"{day} {en[:3]}",
           f"{day} {hi}"] + [f"{day} {alt}" for alt in MONTHS_HI_ALT.get(hi, [])]
    return out


def load_candidates():
    with (ROOT / "data/candidates/candidates.csv").open(encoding="utf-8") as f:
        return {r["cand_id"]: r for r in csv.DictReader(f)}


def main(batch):
    draft = json.loads((ROOT / f"data/items/drafts/{batch}.json").read_text(encoding="utf-8"))
    cands = load_candidates()
    items = draft["items"]
    errors, warnings = [], []
    out = []
    pos_counter = Counter()

    for it in items:
        iid = it["item_id"]
        answerable = it.get("is_answerable", True)
        for lang in LANGS:
            if lang not in it["text"]:
                errors.append(f"{iid}: missing language {lang}")
        if not answerable:
            for lang in LANGS:
                for q in ("q1", "q2"):
                    if not it["text"].get(lang, {}).get(q):
                        errors.append(f"{iid}/{lang}: missing {q}")
            out.append({**it, "drafted_by": draft["drafted_by"]})
            continue

        # Gold aliases (expand dates).
        gold = it["gold"]
        if "date" in gold:
            gold["slots"] = [{"name": "date", "aliases": date_aliases(gold["date"]["day"], gold["date"]["month"])}]
        dis = it.get("distractor", {})
        if "date" in dis:
            dis["value_aliases"] = date_aliases(dis["date"]["day"], dis["date"]["month"])

        for lang in LANGS:
            t = it["text"][lang]
            for fld in TURN_FIELDS + ("q1", "q2"):
                if not t.get(fld):
                    errors.append(f"{iid}/{lang}: missing {fld}")
            # 1) Every slot is stated in the memory turn.
            for slot in gold["slots"]:
                if not any(contains(t["memory_turn"], a) for a in slot["aliases"]):
                    errors.append(f"{iid}/{lang}: slot '{slot['name']}' not found in memory_turn")
            # 2) No leakage of the gold value outside the memory turn.
            for fld in ("assistant_reply", "followup_turn", "followup_reply", "q1", "q2", "q3"):
                for slot in gold["slots"]:
                    hit = [a for a in slot["aliases"] if contains(t.get(fld, ""), a)]
                    if hit:
                        errors.append(f"{iid}/{lang}: gold alias {hit[0]!r} leaks into {fld}")
            # 3) Distractor sanity.
            if it.get("has_distractor"):
                ds = t.get("distractor_sentence", "")
                if not ds:
                    errors.append(f"{iid}/{lang}: has_distractor but no distractor_sentence")
                elif not any(contains(ds, a) for a in dis.get("value_aliases", [])):
                    errors.append(f"{iid}/{lang}: distractor value not found in distractor_sentence")
                for slot in gold["slots"]:
                    if any(contains(ds, a) for a in slot["aliases"]):
                        errors.append(f"{iid}/{lang}: gold value appears inside distractor_sentence")
            # 4) Gender agreement in the user's own turns.
            if lang in ("hi", "hg"):
                wrong = MASC[lang] if it["user_gender"] == "female" else FEM[lang]
                for fld in ("memory_turn", "followup_turn", "q1", "q2", "q3"):
                    m = wrong.search(t.get(fld, ""))
                    if m:
                        errors.append(f"{iid}/{lang}: '{m.group(0)}' in {fld} contradicts user_gender={it['user_gender']}")
            # 5) Length guidance (warnings only).
            if lang == "en":
                n = len(t["memory_turn"].split())
                if n > 60:
                    warnings.append(f"{iid}: memory_turn has {n} words (> 60)")
                n = len(t["assistant_reply"].split())
                if n > 50:
                    warnings.append(f"{iid}: assistant_reply has {n} words (> 50)")

        # Source info, balanced evidence position, deterministic filler seed.
        c = cands.get(it["cand_id"], {})
        mtype = it["memory_type"]
        pos = POSITIONS[pos_counter[mtype] % len(POSITIONS)]
        pos_counter[mtype] += 1
        seed = int(hashlib.sha256(iid.encode()).hexdigest()[:8], 16)
        out.append({**it,
                    "source": {"dataset": "LongMemEval", "question_id": c.get("lme_qid"), "lme_type": c.get("lme_type")},
                    "topic": c.get("topic"), "is_answerable": True,
                    "evidence_position": pos, "filler_seed": seed,
                    "drafted_by": draft["drafted_by"]})

    # Balance report.
    ans = [i for i in out if i.get("is_answerable", True)]
    bal = Counter((i["memory_type"], i["user_gender"]) for i in ans)
    dis_bal = Counter(i["memory_type"] for i in ans if i.get("has_distractor"))
    pos_bal = Counter((i["memory_type"], i["evidence_position"]) for i in ans)

    report = [f"QA report for {batch}: {len(ans)} answerable + {len(out) - len(ans)} abstention items",
              f"ERRORS: {len(errors)}"] + [f"  {e}" for e in errors] + \
             [f"WARNINGS: {len(warnings)}"] + [f"  {w}" for w in warnings] + \
             ["BALANCE (type, gender): " + str(dict(sorted(bal.items()))),
              "DISTRACTORS per type: " + str(dict(dis_bal)),
              "EVIDENCE POSITION (type, slot): " + str(dict(sorted(pos_bal.items())))]
    (ROOT / f"data/items/qa_{batch}.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    with (ROOT / f"data/items/items_{batch}.jsonl").open("w", encoding="utf-8") as f:
        for it in out:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print("\n".join(report))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "batch01_pilot"))
