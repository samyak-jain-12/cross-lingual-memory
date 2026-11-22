"""Phase 3, step 1b: mine extra preference candidates from LongMemEval-S user turns.

LongMemEval has only 30 preference questions (15 usable), so we need ~33 more (design_spec.md §3.1:
"top up to 50 from preference statements inside other items' user turns"). We scan user turns
in the haystack sessions for explicit preference cues and keep one sentence per unique statement.

Writes data/candidates/pref_extra.csv (team / Claude screens it like candidates.csv).
Run from the project root:  python src/mine_preferences.py
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/raw/longmemeval_s_cleaned.json"
OUT = ROOT / "data/candidates/pref_extra.csv"

CUE = re.compile(
    r"\b(my (absolute )?favou?rite|I('m| am) (a )?(big|huge) fan of|I (really |absolutely )?(love|prefer|adore)"
    r"|I('ve| have) always (loved|preferred|enjoyed)|I usually go for|I always (order|go for|use|choose))\b", re.I)
SENT = re.compile(r"(?<=[.!?])\s+")
# Skip cues that are about other people or hypothetical.
SKIP = re.compile(r"\b(my (friend|sister|brother|mom|dad|partner|wife|husband|son|daughter)'s|would love|I'd love|love to)\b", re.I)


def main():
    data = json.loads(SRC.read_text())
    seen, rows = set(), []
    for x in data:
        for sid, sess in zip(x["haystack_session_ids"], x["haystack_sessions"]):
            for turn in sess:
                if turn["role"] != "user" or turn.get("has_answer"):
                    continue
                for s in SENT.split(turn["content"]):
                    s = s.strip()
                    if not (8 <= len(s.split()) <= 40) or not CUE.search(s) or SKIP.search(s):
                        continue
                    key = s.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append({"pcand_id": f"PX{len(rows) + 1:04d}", "session_id": sid,
                                 "cue": CUE.search(s).group(0), "sentence": s,
                                 "turn": turn["content"][:600], "keep": "", "question": "", "answer": "", "notes": ""})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} preference sentences -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
