"""Independent-model verification analysis (Aya Expanse 8B; see src/make_verify.py).

Run from the project root:  python3 src/analyze_verify.py main_r1
Reads  results/<run>/verify/{aya_judge.jsonl, aya_audit.jsonl}, results/<run>/scored.csv, data/items/items_main.jsonl
Writes results/<run>/verify/{verify.md, judge_compare.csv, judge_confusion.csv, audit_parsed.csv, audit_flagged.csv,
       sensitivity_h1.csv}

1. Judge check. The 300 answers were sampled stratified by the Qwen judge's label (126 CORRECT, 63 INCORRECT,
   63 NO_ANSWER on answerable items; 24 ANSWERED, 24 NO_ANSWER on controls). Raw agreement on the sample therefore
   over-weights the rare labels. Population estimates re-weight each stratum to its share of all 41,580 judgments
   (weight = population share / sample count). 95% CIs: stratified bootstrap (10k).
2. Item audit. Aya's JSON verdict per item x language (hi, hg). Core failures: meaning_same = no,
   key_fact_present = no, questions_same = no. "natural" is reported separately (a style judgement).
3. Sensitivity. H1 gaps (mono - cross, item-paired) recomputed without the items that fail a core check
   in either language.
This is independent-model verification, not human verification; report it as such.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN = sys.argv[1] if len(sys.argv) > 1 else "main_r1"
RES = ROOT / "results" / RUN
V = RES / "verify"
NBOOT = 10_000
rng = np.random.default_rng(20261121)
LANGS = ["en", "hi", "hg"]
SETUPS = ["FC", "RM-S1", "RM-S2", "RM-S3", "OR-S1", "OR-S2", "OR-S3"]
LABELS = ["CORRECT", "INCORRECT", "NO_ANSWER", "ANSWERED"]
md = []


def say(*lines):
    md.extend(lines)


def pct(x, nd=1):
    return f"{100 * x:.{nd}f}%"


def table(df, cols=None):
    cols = cols or list(df.columns)
    rows = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df[cols].iterrows():
        rows.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return rows


def kappa(conf):
    """Cohen's kappa from a (possibly weighted) square confusion matrix."""
    conf = np.asarray(conf, float)
    n = conf.sum()
    po = np.trace(conf) / n
    pe = (conf.sum(0) * conf.sum(1)).sum() / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


# ---------------------------------------------------------------- 1. judge
def aya_label(raw):
    m = re.match(r"\W*(CORRECT|INCORRECT|NO_ANSWER|ANSWERED)\b", raw.strip(), re.I)
    return m.group(1).upper() if m else "UNPARSED"


J = pd.DataFrame([json.loads(l) for l in open(V / "aya_judge.jsonl", encoding="utf-8")])
J["aya"] = J["aya_raw"].map(aya_label)
J["agree"] = J["aya"] == J["qwen_judge"]
scored = pd.read_csv(RES / "scored.csv")
pop = scored.groupby(["answerable", "judge"]).size()
pop_share = pop / pop.sum()
n_s = J.groupby(["answerable", "qwen_judge"]).size()
J["w"] = [pop_share[(a, q)] / n_s[(a, q)] for a, q in zip(J["answerable"], J["qwen_judge"])]
# binary view used by the accuracy metric: answerable -> correct or not; controls -> abstained or not
J["qwen_pos"] = np.where(J["answerable"], J["qwen_judge"] == "CORRECT", J["qwen_judge"] == "NO_ANSWER")
J["aya_pos"] = np.where(J["answerable"], J["aya"] == "CORRECT", J["aya"] == "NO_ANSWER")
J["agree_bin"] = J["qwen_pos"] == J["aya_pos"]
J.drop(columns=["aya_raw"]).to_csv(V / "judge_compare.csv", index=False)


def wmean(x, w):
    return float(np.sum(x * w) / np.sum(w))


def strat_boot(sub, fn):
    groups = [g.index.to_numpy() for _, g in sub.groupby(["answerable", "qwen_judge"])]
    vals = []
    for _ in range(NBOOT):
        idx = np.concatenate([rng.choice(g, len(g)) for g in groups])
        vals.append(fn(sub.loc[idx]))
    return np.percentile(vals, 2.5), np.percentile(vals, 97.5)


def wconf(sub, a="qwen_judge", b="aya", labels=LABELS):
    c = np.zeros((len(labels), len(labels)))
    for x, y, w in zip(sub[a], sub[b], sub["w"]):
        if x in labels and y in labels:
            c[labels.index(x), labels.index(y)] += w
    return c


def bin_kappa(sub):
    c = np.zeros((2, 2))
    for x, y, w in zip(sub["qwen_pos"], sub["aya_pos"], sub["w"]):
        c[int(x), int(y)] += w
    return kappa(c)


say(f"# Independent-model verification of `{RUN}` (Aya Expanse 8B)", "",
    "Aya Expanse 8B (Cohere; a different model family from the Qwen judge and both readers) re-labelled a stratified "
    "sample of 300 judge decisions with the judge's exact prompt, and audited every item's Hindi and Hinglish text "
    "against the English source. This is **independent-model verification, not human verification**.", "",
    f"Aya replies parsed: judge {int((J.aya != 'UNPARSED').sum())}/{len(J)}.", "")

say("## 1. Judge agreement", "",
    "Sample stratified by the Qwen label. *Population* figures re-weight each stratum to its share of all "
    f"{len(scored):,} judgments; 95% CI by stratified bootstrap.", "")
strata = []
for (a, q), g in J.groupby(["answerable", "qwen_judge"]):
    vc = g["aya"].value_counts()
    strata.append(dict(items="answerable" if a else "control", qwen=q, n=len(g), population_share=pct(pop_share[(a, q)]),
                       aya_same=pct(g["agree"].mean()),
                       aya_labels=", ".join(f"{k} {v}" for k, v in vc.items())))
say(*table(pd.DataFrame(strata)), "")

rows = []
for name, sub in (("answerable", J[J.answerable]), ("controls", J[~J.answerable]), ("all", J)):
    sub = sub.copy()
    labs = ["CORRECT", "INCORRECT", "NO_ANSWER"] if name == "answerable" else (
        ["ANSWERED", "NO_ANSWER"] if name == "controls" else LABELS)
    ag = wmean(sub.agree, sub.w)
    ag_ci = strat_boot(sub, lambda s: wmean(s.agree, s.w))
    agb = wmean(sub.agree_bin, sub.w)
    agb_ci = strat_boot(sub, lambda s: wmean(s.agree_bin, s.w))
    k = kappa(wconf(sub, labels=labs))
    k_ci = strat_boot(sub, lambda s: kappa(wconf(s, labels=labs)))
    kb = bin_kappa(sub)
    kb_ci = strat_boot(sub, bin_kappa)
    rows.append(dict(set=name, n=len(sub), raw_agree_sample=pct(sub.agree.mean()),
                     pop_agree=f"{pct(ag)} [{pct(ag_ci[0])}, {pct(ag_ci[1])}]",
                     pop_kappa=f"{k:.2f} [{k_ci[0]:.2f}, {k_ci[1]:.2f}]",
                     pop_agree_binary=f"{pct(agb)} [{pct(agb_ci[0])}, {pct(agb_ci[1])}]",
                     pop_kappa_binary=f"{kb:.2f} [{kb_ci[0]:.2f}, {kb_ci[1]:.2f}]"))
say(*table(pd.DataFrame(rows)), "",
    "*binary* = the distinction the accuracy metric uses (answerable: CORRECT vs not; controls: NO_ANSWER vs not).", "")

conf = pd.DataFrame(0, index=LABELS, columns=LABELS + ["UNPARSED"])
for q, a in zip(J.qwen_judge, J.aya):
    conf.loc[q, a] += 1
conf.index.name = "qwen \\ aya"
conf.to_csv(V / "judge_confusion.csv")
say("Confusion on the sample (rows Qwen, columns Aya; raw counts):", "",
    *table(conf.reset_index()), "")

# implied accuracy under each judge, and agreement with the rule-based slot match
A = J[J.answerable].copy()
acc_q = wmean(A.qwen_pos, A.w)
acc_a = wmean(A.aya_pos, A.w)
d_ci = strat_boot(A, lambda s: wmean(s.aya_pos, s.w) - wmean(s.qwen_pos, s.w))
S = A[A.slot_match.notna()]
sm_q = wmean(S.qwen_pos == (S.slot_match == 1), S.w)
sm_a = wmean(S.aya_pos == (S.slot_match == 1), S.w)
say("**Accuracy implied by each judge** (answerable items, population-weighted): "
    f"Qwen {pct(acc_q)}, Aya {pct(acc_a)}; difference Aya − Qwen {100 * (acc_a - acc_q):+.1f}pp "
    f"[{100 * d_ci[0]:+.1f}, {100 * d_ci[1]:+.1f}].", "",
    f"**Agreement with slot match** (rule-based; population-weighted): Qwen {pct(sm_q)}, Aya {pct(sm_a)}.", "")

dis = J[~J.agree].copy()
by_cell = A.assign(cross=np.where(A.store == A["query"], "mono", "cross")).groupby("cross").apply(
    lambda g: pd.Series(dict(n=len(g), agree=pct(g.agree_bin.mean()))), include_groups=False)
say("Binary agreement on the sample by cell type (unweighted): " +
    "; ".join(f"{i} {r.agree} (n={r.n})" for i, r in by_cell.iterrows()), "")

# ---------------------------------------------------------------- 2. audit
FIELDS = ["meaning_same", "key_fact_present", "questions_same", "natural"]


def parse_audit(raw):
    m = re.search(r"\{.*\}", raw, re.S)
    try:
        d = json.loads(m.group(0))
    except Exception:
        return {f: "unparsed" for f in FIELDS} | {"problems": raw[:200]}
    out = {f: str(d.get(f, "missing")).strip().lower() for f in FIELDS}
    out["problems"] = str(d.get("problems", "")).strip()
    return out


AU = pd.DataFrame([json.loads(l) for l in open(V / "aya_audit.jsonl", encoding="utf-8")])
AU = pd.concat([AU.drop(columns=["aya_raw", "fields"]), pd.DataFrame([parse_audit(r) for r in AU.aya_raw])], axis=1)
AU.loc[~AU.answerable & (AU.key_fact_present != "no"), "key_fact_present"] = "n/a"
AU["core_fail"] = (AU.meaning_same == "no") | (AU.key_fact_present == "no") | (AU.questions_same == "no")
AU.to_csv(V / "audit_parsed.csv", index=False)

say("## 2. Item audit (Hindi and Hinglish vs English source)", "",
    f"{len(AU)} audits = {AU.item_id.nunique()} items × 2 languages. Share answered **no** per check:", "")
rows = []
for lang in ("hi", "hg"):
    g = AU[AU.lang == lang]
    r = dict(language=lang, n=len(g))
    for f in FIELDS:
        base = g[g[f] != "n/a"]
        r[f] = f"{int((base[f] == 'no').sum())}/{len(base)}"
    r["any core fail"] = f"{int(g.core_fail.sum())}/{len(g)}"
    rows.append(r)
say(*table(pd.DataFrame(rows)), "")
odd = AU[~AU[FIELDS].isin(["yes", "no", "n/a"]).all(axis=1)]
if len(odd):
    say(f"Non-standard values in {len(odd)} audits (counted as neither yes nor no).", "")

flag = AU[AU.core_fail | (AU.natural == "no")].sort_values(["item_id", "lang"])
flag[["item_id", "lang", "answerable"] + FIELDS + ["problems"]].to_csv(V / "audit_flagged.csv", index=False)
fail_items = sorted(AU[AU.core_fail].item_id.unique())
say(f"Items failing a core check in at least one language: **{len(fail_items)}** "
    f"({', '.join(fail_items) if fail_items else 'none'}). Full list with Aya's notes: `audit_flagged.csv`.", "")
cf = AU[AU.core_fail]
if len(cf):
    say("Core failures with Aya's description:", "")
    for _, r in cf.sort_values(["item_id", "lang"]).iterrows():
        checks = ", ".join(f for f in FIELDS[:3] if r[f] == "no")
        say(f"- {r.item_id} [{r.lang}] {checks}: {r.problems[:220] or '(no description)'}")
    say("")


# ---------------------------------------------------------------- 3. sensitivity
def item_acc(df, cells):
    keys = set(cells)
    sub = df[[(s, q) in keys for s, q in zip(df["store"], df["query"])]]
    return sub.groupby("item_id")["correct"].mean()


def boot_ci(d):
    d = np.asarray(d, float)
    m = d[rng.integers(0, len(d), size=(NBOOT, len(d)))].mean(1)
    return np.percentile(m, 2.5), np.percentile(m, 97.5)


DIAG = [(l, l) for l in LANGS]
CROSS = [(s, q) for s in LANGS for q in LANGS if s != q]
ANS = scored[scored.answerable]
rows = []
for m in sorted(ANS.model.unique()):
    for s in SETUPS:
        sub = ANS[(ANS.model == m) & (ANS.setup == s)]
        mono, cross = item_acc(sub, DIAG), item_acc(sub, CROSS)
        d = (mono - cross).dropna()
        dk = d[~d.index.isin(fail_items)]
        lo, hi = boot_ci(d)
        lk, hk = boot_ci(dk)
        rows.append(dict(model=m, setup=s, gap_all=f"{100 * d.mean():+.1f}pp [{100 * lo:+.1f}, {100 * hi:+.1f}]",
                         n_all=len(d), gap_clean=f"{100 * dk.mean():+.1f}pp [{100 * lk:+.1f}, {100 * hk:+.1f}]",
                         n_clean=len(dk), change=f"{100 * (dk.mean() - d.mean()):+.1f}pp"))
sens = pd.DataFrame(rows)
sens.to_csv(V / "sensitivity_h1.csv", index=False)
say("## 3. Sensitivity: H1 gap without items that fail a core audit check", "",
    f"Gap = mono − cross accuracy, item-paired, 95% bootstrap CI; *clean* drops the {len(fail_items)} items above.", "",
    *table(sens), "")

# ---------------------------------------------------------------- 4. planted-error test of the audit
PROBE = V / "aya_probe.jsonl"
if PROBE.exists():
    P = pd.DataFrame([json.loads(l) for l in open(PROBE, encoding="utf-8")])
    P = pd.concat([P.drop(columns=["aya_raw", "fields"]), pd.DataFrame([parse_audit(r) for r in P.aya_raw])], axis=1)
    P["caught_expected"] = [any(r[f] == "no" for f in r.expected_fail) for _, r in P.iterrows()]
    P["caught_any"] = (P[FIELDS[:3]] == "no").any(axis=1)
    P.to_csv(V / "audit_probe_scored.csv", index=False)
    rows = [dict(group=k, n=len(g), caught_expected_check=f"{int(g.caught_expected.sum())}/{len(g)}",
                 caught_any_core_check=f"{int(g.caught_any.sum())}/{len(g)}")
            for k, g in [*P.groupby("corruption"), *P.groupby("lang"), ("all", P)]]
    say("## 4. Planted-error test of the audit (`src/make_audit_probe.py`)", "",
        f"{len(P)} deliberately broken translations (key fact swapped or deleted, q1 or memory_turn replaced by another "
        "item's) in the exact audit prompt. *Caught* = Aya answers no to a check the corruption breaks.", "",
        *table(pd.DataFrame(rows)), "",
        f"**Detection rate {pct(P.caught_expected.mean())}.** The audit cannot tell broken translations from good ones, "
        "so its 330/330 pass is **not evidence of translation quality** and is not reported as such.", "")

(V / "verify.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
