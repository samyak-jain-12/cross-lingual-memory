"""Error taxonomy sample (design_spec §6.3): 150 errors, stratified.

Run from the project root:  python3 src/make_error_sample.py main_r1
Population: answerable observations judged not CORRECT in the main block.
Strata: reader (2) x setup group (FC / RM / OR) x cell (mono / cross) = 12; 13 per cross stratum, 12 per mono
stratum (150), at most one error per item within a stratum, seed 20261122.
Automatic codes from scored.csv: E6 false abstention (abstained), E4 distractor capture (distractor_capture);
everything else is labelled by hand in error_labels.csv (sid, code, note).
Writes results/<run>/analysis/error_sample.csv
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN = sys.argv[1] if len(sys.argv) > 1 else "main_r1"
OUT = ROOT / "results" / RUN / "analysis"
SEED = 20261122

items = {j["item_id"]: j for j in map(json.loads, open(ROOT / "data/items/items_main.jsonl", encoding="utf-8"))}
d = pd.read_csv(ROOT / "results" / RUN / "scored.csv")
e = d[d.answerable & ~d.correct.astype(bool)].copy()
e["grp"] = e.setup.str[:2]
e["cell"] = np.where(e.store == e["query"], "mono", "cross")
parts = []
for (m, g, c), s in e.groupby(["model", "grp", "cell"]):
    s = s.sample(frac=1, random_state=SEED).drop_duplicates("item_id")
    parts.append(s.head(13 if c == "cross" else 12))
S = pd.concat(parts).reset_index(drop=True)
S["stratum_pop"] = S.groupby(["model", "grp", "cell"])["item_id"].transform("size")
pop = e.groupby(["model", "grp", "cell"]).size().rename("pop_n")
S = S.join(pop, on=["model", "grp", "cell"])
S["weight"] = S["pop_n"] / S["stratum_pop"]
S.insert(0, "sid", [f"X{i:03d}" for i in range(len(S))])
S["question"] = [items[i]["text"][q][v] for i, q, v in zip(S.item_id, S["query"], S.qv)]
S["gold"] = [items[i]["gold"]["answer_en"] for i in S.item_id]
S["distractor"] = [", ".join(items[i].get("distractor", {}).get("value_aliases", [])[:2]) if items[i].get("distractor")
                   else "" for i in S.item_id]
S["auto_code"] = np.where(S.abstained.astype(bool), "E6", np.where(S.distractor_capture.astype(bool), "E4", ""))
cols = ["sid", "model", "setup", "grp", "cell", "store", "query", "qv", "item_id", "memory_type", "judge", "slot_match",
        "abstained", "distractor_capture", "near_miss_capture", "resp_lang", "gold_rank", "auto_code", "question", "gold",
        "distractor", "response", "pop_n", "weight"]
S[cols].to_csv(OUT / "error_sample.csv", index=False)
print(f"{len(S)} errors sampled; auto-coded {int((S.auto_code != '').sum())} "
      f"(E6 {int((S.auto_code == 'E6').sum())}, E4 {int((S.auto_code == 'E4').sum())}); "
      f"{int((S.auto_code == '').sum())} to label by hand")
