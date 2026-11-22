"""Error taxonomy tables (design_spec §6.3; sample from src/make_error_sample.py).

Run from the project root:  python3 src/analyze_errors.py main_r1
Reads  results/<run>/analysis/{error_sample.csv, error_labels.csv}
Writes results/<run>/analysis/{error_taxonomy.csv, error_taxonomy.md}

Final code = manual label if present (error_labels.csv overrides the automatic code), else the automatic code
(E6 abstained, E4 distractor_capture). Codes E1-E8 are the spec's; E9 (off-task / degenerate output) and OK
(answer is actually correct, i.e. a judge false negative) were added while labelling (DEVIATIONS #15).
Labelled by one annotator (Claude, an AI assistant); no inter-annotator agreement. Shares are given raw and
re-weighted to the population of errors per stratum (reader x setup group x mono/cross).
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN = sys.argv[1] if len(sys.argv) > 1 else "main_r1"
A = ROOT / "results" / RUN / "analysis"
NAMES = {"E1": "entity substitution", "E2": "number / date altered", "E3": "polarity / preference inversion",
         "E4": "distractor capture", "E5": "transliteration corruption", "E6": "false abstention",
         "E7": "unsupported content", "E8": "partial answer", "E9": "off-task / degenerate output",
         "OK": "actually correct (judge false negative)"}

S = pd.read_csv(A / "error_sample.csv", keep_default_na=False)
L = pd.read_csv(A / "error_labels.csv", keep_default_na=False)
S = S.merge(L, on="sid", how="left").fillna({"code": "", "note": ""})
S["final"] = [c if c else a for c, a in zip(S.code, S.auto_code)]
assert (S.final != "").all(), S[S.final == ""].sid.tolist()
S["source"] = ["manual" if c else "auto" for c in S.code]
S.to_csv(A / "error_taxonomy.csv", index=False)


def shares(df):
    raw = df.final.value_counts()
    w = df.groupby("final").weight.sum() / df.weight.sum()
    return raw, w


md = [f"# Error taxonomy on `{RUN}` ({len(S)} sampled errors)", "",
      "Stratified sample of answerable responses judged not CORRECT (reader × FC/RM/OR × mono/cross; 12–13 each, "
      "one error per item per stratum). E4 and E6 are automatic unless overridden; the rest were labelled by hand by "
      "one annotator (Claude, an AI assistant), so no inter-annotator agreement is reported. *Weighted* re-weights "
      "each stratum to its share of all 2,386 errors.", ""]
raw, w = shares(S)
rows = ["| code | error | n | raw | weighted |", "|---|---|---|---|---|"]
for c in NAMES:
    if c in raw:
        rows.append(f"| {c} | {NAMES[c]} | {raw[c]} | {100 * raw[c] / len(S):.0f}% | {100 * w[c]:.0f}% |")
md += rows + [""]

for by, title in (("cell", "mono vs cross-lingual cells"), ("grp", "setup group"), ("model", "reader")):
    t = pd.crosstab(S.final, S[by], values=S.weight, aggfunc="sum", normalize="columns").reindex(NAMES).dropna(how="all")
    n = S[by].value_counts()
    cols = list(t.columns)
    md += [f"### By {title} (weighted share within each column)", "",
           "| code | " + " | ".join(f"{c} (n={n[c]})" for c in cols) + " |", "|---|" + "---|" * len(cols)]
    for c, r in t.fillna(0).iterrows():
        md.append(f"| {c} {NAMES[c]} | " + " | ".join(f"{100 * v:.0f}%" for v in r) + " |")
    md.append("")

overr = S[(S.source == "manual") & (S.auto_code != "") & (S.code != S.auto_code)]
missed = S[(S.source == "manual") & (S.auto_code == "") & S.code.isin(["E4", "E6"])]
md += ["### Notes", "",
       f"- Automatic codes overridden by hand: {len(overr)} ({', '.join(overr.sid) or 'none'}).",
       f"- E4/E6 cases the automatic flags missed (transliterated distractors, refusals not caught by the regex): "
       f"{len(missed)}.",
       f"- {int((S.final == 'OK').sum())} of {len(S)} sampled 'errors' are correct answers the judge rejected "
       "(e.g. नाइके = Nike, a correct ratio or count, or the gold plus extra advice).", ""]
(A / "error_taxonomy.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
