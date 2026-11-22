"""Pre-registered analysis of the main run and its ablations [design_spec 1, 6; ENDSEM_PLAN 1].

Run from the project root:  python3 src/analyze_main.py main_r1
Reads  results/<run>/{scored.csv, abl_*/scored.csv, table_recall.csv}, data/items/items_main.jsonl
Writes results/<run>/analysis/*.csv and analysis.md (read-only on the run's own files).

Unit of analysis: the item, always paired across conditions. Item accuracy in a condition = mean over its
observations in that condition (cells x paraphrases). alpha = .05 two-sided, Holm inside each family:
  H1  one family per reader (7 setups)          paired sign-flip permutation test on item gaps (10k)
  H2  one family per reader x setup (3 pairs)    exact McNemar on items (item better in A vs in B)
  H3  one family per reader x setup (3 pairs)    exact McNemar on items, two-sided
  H4  one family per reader x setup group        Cochran's Q over S1/S2/S3 + pairwise McNemar (Holm)
Gaps smaller than the paraphrase noise floor are flagged.
"""
import json
import sys
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RUN = sys.argv[1] if len(sys.argv) > 1 else "main_r1"
RES = ROOT / "results" / RUN
OUT = RES / "analysis"
LANGS = ["en", "hi", "hg"]
DIAG = [(l, l) for l in LANGS]
CROSS = [(s, q) for s in LANGS for q in LANGS if s != q]
NPERM = NBOOT = 10_000
rng = np.random.default_rng(20261120)
md = []


def say(*lines):
    md.extend(lines)


def holm(ps):
    ps = np.asarray(ps, float)
    order = np.argsort(ps)
    adj = np.empty_like(ps)
    run = 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - k) * ps[i]))
        adj[i] = run
    return adj


def mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def perm_test(d):
    """Two-sided paired sign-flip permutation test on per-item differences d."""
    d = np.asarray(d, float)
    obs = abs(d.mean())
    signs = rng.choice([-1.0, 1.0], size=(NPERM, len(d)))
    return (np.sum(np.abs((signs * d).mean(1)) >= obs - 1e-12) + 1) / (NPERM + 1)


def boot_ci(d):
    d = np.asarray(d, float)
    idx = rng.integers(0, len(d), size=(NBOOT, len(d)))
    m = d[idx].mean(1)
    return np.percentile(m, 2.5), np.percentile(m, 97.5)


def item_acc(df, cells, **eq):
    """Per-item accuracy over the given (store, query) cells, after filtering columns by eq."""
    sub = df
    for k, v in eq.items():
        sub = sub[sub[k] == v]
    keys = set(cells)
    sub = sub[[(s, q) in keys for s, q in zip(sub["store"], sub["query"])]]
    return sub.groupby("item_id")["correct"].mean()


def paired(a, b):
    j = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    return j["a"], j["b"]


def pct(x, nd=1):
    return f"{100 * x:.{nd}f}%"


def pp(x, nd=1):
    return f"{100 * x:+.{nd}f}pp"


def fmt_p(p):
    return "<.001" if p < 0.001 else f"{p:.3f}"


def table(df, cols=None):
    cols = cols or list(df.columns)
    rows = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df[cols].iterrows():
        rows.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return rows


# ---------------------------------------------------------------- load
items = {j["item_id"]: j for j in map(json.loads, open(ROOT / "data/items/items_main.jsonl"))}


def load(block):
    d = pd.read_csv(RES / ("scored.csv" if block == "main" else f"abl_{block}/scored.csv"))
    d["evidence_class"] = d["item_id"].map(lambda i: items[i].get("evidence_class"))
    d["has_distractor"] = d["item_id"].map(lambda i: items[i].get("has_distractor"))
    return d


ALL = load("main")
A = ALL[ALL["answerable"]].copy()
C = ALL[~ALL["answerable"]].copy()
MODELS = sorted(A["model"].unique())
SETUPS = ["FC", "RM-S1", "RM-S2", "RM-S3", "OR-S1", "OR-S2", "OR-S3"]
OUT.mkdir(exist_ok=True)

say(f"# Analysis of `{RUN}` (pre-registered tests, design_spec §1)", "",
    f"Answerable items: {A['item_id'].nunique()} · controls: {C['item_id'].nunique()} · readers: {', '.join(MODELS)}",
    "Item accuracy in a condition = mean over its cells × paraphrases. α = .05 two-sided, Holm within each family.", "")

# ---------------------------------------------------------------- noise floor
nf = {}
for m in MODELS:
    for s in SETUPS:
        sub = A[(A["model"] == m) & (A["setup"] == s) & (A["store"] == A["query"])]
        w = sub.pivot_table(index=["item_id", "store"], columns="qv", values="correct")
        nf[(m, s)] = float((w["q1"] != w["q2"]).mean())
        # Scale-matched floor (DEVIATIONS #13): the item-paired accuracy difference between the two
        # paraphrases on monolingual cells, i.e. how far apart two equivalent wordings land in mean accuracy.
        pw = w.groupby(level="item_id").mean()
        dq = pw["q1"] - pw["q2"]
        lo, hi = boot_ci(dq)
        nf[(m, s, "para")] = (abs(float(dq.mean())), max(abs(lo), abs(hi)))

# ---------------------------------------------------------------- H1
rows = []
for m in MODELS:
    fam = []
    for s in SETUPS:
        mono, cross = paired(item_acc(A, DIAG, model=m, setup=s), item_acc(A, CROSS, model=m, setup=s))
        d = mono - cross
        lo, hi = boot_ci(d)
        fam.append(dict(model=m, setup=s, n_items=len(d), mono=mono.mean(), cross=cross.mean(), gap=d.mean(),
                        ci_lo=lo, ci_hi=hi, p_perm=perm_test(d), noise_floor=nf[(m, s)],
                        para_diff=nf[(m, s, "para")][0], para_ci_edge=nf[(m, s, "para")][1]))
    for r, ph in zip(fam, holm([r["p_perm"] for r in fam])):
        r["p_holm"] = ph
        r["verdict"] = "supported" if r["gap"] > 0 and ph < 0.05 else "not significant"
        r["below_disagreement_floor"] = abs(r["gap"]) < r["noise_floor"]
        r["exceeds_paraphrase_noise"] = r["ci_lo"] > r["para_ci_edge"]
    rows += fam
h1 = pd.DataFrame(rows)
h1.to_csv(OUT / "h1_gap.csv", index=False)

# H1 second clause: is the drop larger for retrieval (RM-S1) than for full context?
h1b = []
for m in MODELS:
    def gap_items(s):
        a, b = paired(item_acc(A, DIAG, model=m, setup=s), item_acc(A, CROSS, model=m, setup=s))
        return a - b
    d = (gap_items("RM-S1") - gap_items("FC")).dropna()
    lo, hi = boot_ci(d)
    h1b.append(dict(model=m, contrast="gap(RM-S1) - gap(FC)", diff=d.mean(), ci_lo=lo, ci_hi=hi, p_perm=perm_test(d)))
h1b = pd.DataFrame(h1b)
h1b["p_holm"] = holm(h1b["p_perm"])
h1b.to_csv(OUT / "h1_retrieval_vs_fc.csv", index=False)

say("## H1: cross-lingual cells score lower than monolingual cells", "",
    "Gap = mono − cross, item-paired; 95% bootstrap CI; paired permutation test (10k); Holm over the 7 setups per reader.",
    "Noise floors on monolingual cells: *disagree* = P(q1 ≠ q2) per observation (the spec's rule; every gap here is below it, "
    "but it is a per-answer flip rate, not a difference in means); *para* = |acc(q1) − acc(q2)| item-paired, with the outer edge of "
    "its 95% CI. A gap 'beats paraphrase noise' when its CI lower bound is above that edge (DEVIATIONS #13).", "")
t = h1.assign(mono=h1.mono.map(pct), cross=h1.cross.map(pct), gap=h1.gap.map(pp),
              CI=[f"[{100 * a:+.1f}, {100 * b:+.1f}]" for a, b in zip(h1.ci_lo, h1.ci_hi)],
              p=h1.p_holm.map(fmt_p), disagree=h1.noise_floor.map(pct),
              para=[f"{100 * a:.1f} (≤{100 * b:.1f})" for a, b in zip(h1.para_diff, h1.para_ci_edge)],
              beats_para=np.where(h1.exceeds_paraphrase_noise, "yes", "no"))
say(*table(t, ["model", "setup", "mono", "cross", "gap", "CI", "p", "verdict", "disagree", "para", "beats_para"]), "")
say("**Second clause (drop larger for retrieval than full context):** gap(RM-S1) − gap(FC), item-paired, Holm over readers.", "")
for _, r in h1b.iterrows():
    say(f"- {r.model}: {pp(r['diff'])} [{100 * r.ci_lo:+.1f}, {100 * r.ci_hi:+.1f}], p_holm = {fmt_p(r.p_holm)}")
say("")


# ---------------------------------------------------------------- McNemar on items helper
def item_mcnemar(m, s, cell_a, cell_b, df=A):
    a, b = paired(item_acc(df, [cell_a], model=m, setup=s), item_acc(df, [cell_b], model=m, setup=s))
    nb, nc = int((a > b).sum()), int((b > a).sum())
    d = a - b
    lo, hi = boot_ci(d)
    return dict(items=len(d), acc_A=a.mean(), acc_B=b.mean(), diff=d.mean(), ci_lo=lo, ci_hi=hi,
                A_better=nb, B_better=nc, p_exact=mcnemar(nb, nc))


def family(pairs, name, out):
    rows = []
    for m in MODELS:
        for s in SETUPS:
            fam = []
            for (ca, cb) in pairs:
                r = item_mcnemar(m, s, ca, cb)
                r.update(model=m, setup=s, A=f"{ca[0]}→{ca[1]}", B=f"{cb[0]}→{cb[1]}")
                fam.append(r)
            for r, ph in zip(fam, holm([r["p_exact"] for r in fam])):
                r["p_holm"] = ph
            rows += fam
    df = pd.DataFrame(rows)
    df.to_csv(OUT / out, index=False)
    return df


def family_md(df, header, note):
    say(header, "", note, "")
    t = df.assign(acc_A=df.acc_A.map(pct), acc_B=df.acc_B.map(pct), diff=df["diff"].map(pp),
                  CI=[f"[{100 * a:+.1f}, {100 * b:+.1f}]" for a, b in zip(df.ci_lo, df.ci_hi)],
                  wins=[f"{a}/{b}" for a, b in zip(df.A_better, df.B_better)], p=df.p_holm.map(fmt_p),
                  sig=np.where(df.p_holm < 0.05, "✓", ""))
    say(*table(t, ["model", "setup", "A", "B", "acc_A", "acc_B", "diff", "CI", "wins", "p", "sig"]), "")


# ---------------------------------------------------------------- H2
h2 = family([(("hi", "en"), ("en", "hi")), (("hg", "en"), ("en", "hg")), (("hg", "hi"), ("hi", "hg"))], "H2", "h2_mirror.csv")
family_md(h2, "## H2: X→EN beats EN→X (mirrored directions)",
          "Exact McNemar on items (wins = items better in A / better in B); Holm over the 3 pairs within reader × setup. "
          "(The Kaggle `table_mirror.csv` applied Holm over all 42 tests; this table follows the spec.)")

# ---------------------------------------------------------------- H3
h3 = family([(("en", "hg"), ("en", "hi")), (("hi", "hg"), ("hi", "hi")), (("hg", "hg"), ("hi", "hi"))], "H3", "h3_hinglish_query.csv")
family_md(h3, "## H3: Hinglish queries vs Devanagari Hindi queries (two-sided)",
          "Pairs from the spec: EN→HG vs EN→HI, HI→HG vs HI→HI, HG→HG vs HI→HI. Exact McNemar on items, Holm within reader × setup.")

# ---------------------------------------------------------------- H4
h4rows, h4pair = [], []
for m in MODELS:
    for grp in ("RM", "OR"):
        sets = [f"{grp}-S{i}" for i in (1, 2, 3)]
        accs = [item_acc(A, CROSS, model=m, setup=s) for s in sets]
        j = pd.concat(accs, axis=1, keys=sets).dropna()
        # Cochran's Q on binary units (item x cross cell x paraphrase), the spec's test.
        sub = A[(A["model"] == m) & (A["setup"].isin(sets)) & (A["store"] != A["query"])]
        w = sub.pivot_table(index=["item_id", "store", "query", "qv"], columns="setup", values="correct").dropna()
        X = w[sets].to_numpy()
        k = X.shape[1]
        T, R = X.sum(0), X.sum(1)
        Q = (k - 1) * (k * (T ** 2).sum() - T.sum() ** 2) / (k * R.sum() - (R ** 2).sum()) if (k * R.sum() - (R ** 2).sum()) else 0.0
        pq = float(stats.chi2.sf(Q, k - 1))
        # Robustness: Friedman on item means (respects item clustering).
        fr = stats.friedmanchisquare(*[j[s] for s in sets])
        h4rows.append(dict(model=m, group=grp, **{f"acc_{s}": j[s].mean() for s in sets}, cochran_Q=Q, p_Q=pq,
                           friedman_chi2=fr.statistic, p_friedman=fr.pvalue))
        fam = []
        for a, b in (("S3", "S1"), ("S2", "S1"), ("S3", "S2")):
            r = {}
            x, y = j[f"{grp}-{a}"], j[f"{grp}-{b}"]
            nb, nc = int((x > y).sum()), int((y > x).sum())
            lo, hi = boot_ci(x - y)
            fam.append(dict(model=m, group=grp, A=f"{grp}-{a}", B=f"{grp}-{b}", diff=(x - y).mean(), ci_lo=lo, ci_hi=hi,
                            A_better=nb, B_better=nc, p_exact=mcnemar(nb, nc)))
        for r, ph in zip(fam, holm([r["p_exact"] for r in fam])):
            r["p_holm"] = ph
        h4pair += fam
h4 = pd.DataFrame(h4rows)
h4p = pd.DataFrame(h4pair)
h4.to_csv(OUT / "h4_strategies.csv", index=False)
h4p.to_csv(OUT / "h4_pairwise.csv", index=False)

say("## H4: memory representation on cross-lingual cells (S3 dual ≥ S2 pivot > S1 original)", "",
    "Accuracy pooled over the 6 cross-lingual cells. Cochran's Q on (item × cell × paraphrase) units as in the spec; "
    "Friedman on item means as a clustering-robust check; pairwise exact McNemar on items with Holm (3 pairs).", "")
rows = []
for _, r in h4.iterrows():
    g = r.group
    rows.append(dict(model=r.model, group=g, S1=pct(r[f"acc_{g}-S1"]), S2=pct(r[f"acc_{g}-S2"]), S3=pct(r[f"acc_{g}-S3"]),
                     Q=f"{r.cochran_Q:.1f}", p_Q=fmt_p(r.p_Q), p_Friedman=fmt_p(r.p_friedman)))
say(*table(pd.DataFrame(rows)), "")
t = h4p.assign(diff=h4p["diff"].map(pp), CI=[f"[{100 * a:+.1f}, {100 * b:+.1f}]" for a, b in zip(h4p.ci_lo, h4p.ci_hi)],
               wins=[f"{a}/{b}" for a, b in zip(h4p.A_better, h4p.B_better)], p=h4p.p_holm.map(fmt_p),
               sig=np.where(h4p.p_holm < 0.05, "✓", ""))
say(*table(t, ["model", "A", "B", "diff", "CI", "wins", "p", "sig"]), "")

# Recall@5 per strategy pooled over cross cells (BGE-M3 is the RM retriever).
rec = pd.read_csv(RES / "table_recall.csv")
rec = rec[[s != q for s, q in zip(rec["store"], rec["query"])]]
rp = rec.groupby(["retriever", "strategy"])[["R@1", "R@5"]].mean().reset_index()
rp.to_csv(OUT / "h4_recall_cross.csv", index=False)
say("Recall on cross-lingual cells (mean over the 6 cells):", "")
say(*table(rp.assign(**{"R@1": rp["R@1"].map(pct), "R@5": rp["R@5"].map(pct)})), "")


# "S2 loses on names and numbers": S2 - S1 split by the gold slot kind.
def slot_kind(i):
    al = [a for sl in items[i]["gold"]["slots"] for a in sl["aliases"]]
    return "number/date" if any(any(ch.isdigit() for ch in a) for a in al) else "name/other"


A["slot_kind"] = A["item_id"].map(slot_kind)
rows = []
for m in MODELS:
    for kind in ("number/date", "name/other"):
        sub = A[A["slot_kind"] == kind]
        s1, s2 = paired(item_acc(sub, CROSS, model=m, setup="RM-S1"), item_acc(sub, CROSS, model=m, setup="RM-S2"))
        d = s2 - s1
        lo, hi = boot_ci(d)
        rows.append(dict(model=m, slot_kind=kind, items=len(d), S1=s1.mean(), S2=s2.mean(), diff=d.mean(), ci_lo=lo, ci_hi=hi,
                         p=mcnemar(int((s2 > s1).sum()), int((s1 > s2).sum()))))
h4k = pd.DataFrame(rows)
h4k.to_csv(OUT / "h4_pivot_by_slot_kind.csv", index=False)
say("S2 pivot minus S1 original on cross-lingual cells, by gold slot kind (tests 'S2 loses on names and numbers'):", "")
say(*table(h4k.assign(S1=h4k.S1.map(pct), S2=h4k.S2.map(pct), diff=h4k["diff"].map(pp),
                      CI=[f"[{100 * a:+.1f}, {100 * b:+.1f}]" for a, b in zip(h4k.ci_lo, h4k.ci_hi)], p=h4k.p.map(fmt_p)),
           ["model", "slot_kind", "items", "S1", "S2", "diff", "CI", "p"]), "")

# ---------------------------------------------------------------- diagnostic: where it fails
st = pd.read_csv(RES / "table_stages.csv")
st["cell"] = np.where(st["store"] == st["query"], "mono", "cross")
dg = st.groupby(["model", "strategy", "cell"])[["retrieval_miss", "reading_error_given_hit", "oracle_error", "end_to_end_error"]].mean().reset_index()
dg.to_csv(OUT / "diagnostic_stages.csv", index=False)
say("## Diagnostic: retrieval vs reading", "", "Mean over cells (mono = 3 diagonal, cross = 6 off-diagonal); from `table_stages.csv`.", "")
say(*table(dg.assign(**{c: dg[c].map(pct) for c in ["retrieval_miss", "reading_error_given_hit", "oracle_error", "end_to_end_error"]})), "")

# ---------------------------------------------------------------- secondary descriptives
rows = []
for m in MODELS:
    for s in ("FC", "RM-S1"):
        for key in ("memory_type", "evidence_class", "has_distractor"):
            for v, sub in A[(A.model == m) & (A.setup == s)].groupby(key):
                mono, cross = paired(item_acc(sub, DIAG), item_acc(sub, CROSS))
                rows.append(dict(model=m, setup=s, factor=key, level=str(v), items=len(mono), mono=mono.mean(),
                                 cross=cross.mean(), gap=(mono - cross).mean()))
sec = pd.DataFrame(rows)
sec.to_csv(OUT / "breakdown_type_position_distractor.csv", index=False)
say("## Breakdowns (descriptive): memory type, evidence position, distractor", "")
say(*table(sec.assign(mono=sec.mono.map(pct), cross=sec.cross.map(pct), gap=sec.gap.map(pp))), "")

dc = A[A.has_distractor == True]
dc = dc.assign(cell=np.where(dc.store == dc["query"], "mono", "cross"))
dc = dc.groupby(["model", "setup", "cell"]).agg(distractor_capture=("distractor_capture", "mean"),
                                                 n=("distractor_capture", "size")).reset_index()
dc.to_csv(OUT / "distractor_capture.csv", index=False)

fa = A.assign(cell=np.where(A.store == A["query"], "mono", "cross")).groupby(["model", "setup", "cell"])["abstained"].mean().unstack()
fa.to_csv(OUT / "false_abstention.csv")
say("False abstention on answerable items (share of answers that say 'I don't know'):", "")
fa2 = fa.reset_index()
say(*table(fa2.assign(mono=fa2["mono"].map(pct), cross=fa2["cross"].map(pct)), ["model", "setup", "mono", "cross"]), "")

hc = C.assign(cell=np.where(C.store == C["query"], "mono", "cross"),
              halluc=(C["judge"] == "ANSWERED").astype(float) if "ANSWERED" in set(C["judge"]) else 1 - C["correct"])
hc = hc.groupby(["model", "setup", "cell"])["halluc"].mean().unstack().reset_index()
hc.to_csv(OUT / "controls_hallucination.csv", index=False)
say("Hallucination on the 15 unanswerable controls (share of answers giving a specific answer):", "")
say(*table(hc.assign(mono=hc["mono"].map(pct), cross=hc["cross"].map(pct)), ["model", "setup", "mono", "cross"]), "")

rl = A.groupby(["model", "query", "store"])["resp_lang"].value_counts(normalize=True).unstack(fill_value=0).reset_index()
rl.to_csv(OUT / "response_language_by_store.csv", index=False)
say("Response language by query and storage language (share of answers):", "")
say(*table(rl.assign(**{c: rl[c].map(pct) for c in rl.columns if c in ("en", "hi", "hg", "other")})), "")

# ---------------------------------------------------------------- judge check (no human labels yet)
rows = []
for m in MODELS:
    sub = A[A.model == m]
    j, s = sub["correct"].astype(int), sub["slot_match"].astype(int)
    po = float((j == s).mean())
    pe = float(j.mean() * s.mean() + (1 - j.mean()) * (1 - s.mean()))
    rows.append(dict(model=m, n=len(sub), judge_correct=j.mean(), slot_match=s.mean(), agreement=po,
                     kappa=(po - pe) / (1 - pe), judge_yes_slot_no=int(((j == 1) & (s == 0)).sum()),
                     judge_no_slot_yes=int(((j == 0) & (s == 1)).sum())))
jc = pd.DataFrame(rows)
jc.to_csv(OUT / "judge_vs_slot.csv", index=False)
say("## Judge check (judge vs deterministic slot match; human validation not done)", "")
say(*table(jc.assign(judge_correct=jc.judge_correct.map(pct), slot_match=jc.slot_match.map(pct),
                     agreement=jc.agreement.map(pct), kappa=jc.kappa.map(lambda x: f"{x:.3f}"))), "")

# ---------------------------------------------------------------- ablations
say("## Ablations (paired with the main run on the same items)", "")


def abl_compare(block, setups, cells_note, base_filter, abl_filter=lambda d: d, label=("main", "ablation")):
    B = load(block)
    rows = []
    for m in MODELS:
        for s in setups:
            for cell_name, cells in (("mono", DIAG), ("cross", CROSS), ("all", DIAG + CROSS)):
                base = base_filter(A[(A.model == m) & (A.setup == s)])
                ab = abl_filter(B[(B.model == m) & (B.setup == s)])
                cells_here = [c for c in cells if c in set(zip(ab.store, ab["query"]))]
                if not cells_here:
                    continue
                x, y = paired(item_acc(ab, cells_here), item_acc(base, cells_here))
                d = x - y
                lo, hi = boot_ci(d)
                rows.append(dict(model=m, setup=s, cells=cell_name, items=len(d), **{label[1]: x.mean(), label[0]: y.mean()},
                                 diff=d.mean(), ci_lo=lo, ci_hi=hi, p_perm=perm_test(d)))
    df = pd.DataFrame(rows)
    df["p_holm"] = holm(df["p_perm"])
    df.to_csv(OUT / f"ablation_{block}.csv", index=False)
    say(cells_note, "")
    say(*table(df.assign(**{label[1]: df[label[1]].map(pct), label[0]: df[label[0]].map(pct)}, diff=df["diff"].map(pp),
                         CI=[f"[{100 * a:+.1f}, {100 * b:+.1f}]" for a, b in zip(df.ci_lo, df.ci_hi)], p=df.p_holm.map(fmt_p)),
               ["model", "setup", "cells", "items", label[1], label[0], "diff", "CI", "p"]), "")
    return df


abl_compare("short", ["FC", "RM-S1", "RM-S3"],
            "**A. History length:** Short (10 sessions) vs main (20 sessions), 60 items, q1 only. diff = short − long. "
            "Holm over all rows of the table.",
            base_filter=lambda d: d[d.qv == "q1"], label=("long_20", "short_10"))
abl_compare("q3", ["FC", "RM-S1", "RM-S2", "RM-S3"],
            "**B. Indirect questions:** q3 vs q1 (main), 51 items. diff = q3 − q1. Holm over all rows.",
            base_filter=lambda d: d[d.qv == "q1"], label=("direct_q1", "indirect_q3"))
abl_compare("digits", ["FC", "RM-S1", "RM-S2", "RM-S3"],
            "**C. Devanagari digits:** Hindi storage written with १४-style digits vs Latin digits (main), 50 events, q1. "
            "Cells are HI→EN/HI/HG only; 'mono' = HI→HI. diff = Devanagari − Latin. Holm over all rows.",
            base_filter=lambda d: d[(d.qv == "q1") & (d.store == "hi")], label=("latin_digits", "devanagari_digits"))

(OUT / "analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(f"wrote {OUT}/analysis.md and {len(list(OUT.glob('*.csv')))} csv files")
