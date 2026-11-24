"""Paper figures for the main run (static PDF + PNG, light mode).

Run from the project root with a Python that has matplotlib (not installed system-wide; use a venv):
    <venv>/bin/python src/make_figures.py main_r1
Reads results/<run>/{scored.csv, analysis/h1_gap.csv, analysis/h4_recall_cross.csv, analysis/error_taxonomy.csv}
Writes report/figures/fig{1..4}_*.{pdf,png}
With --blog, writes plain-language versions for the blog post instead (report/figures/fig{1..4}_*_blog.png):
no codes like FC / RM-S1 / H1 / CI, axis labels in everyday words.

Colours: reference data-viz palette (categorical slots in fixed order; one-hue blue ramp for magnitude).
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
RUN = ARGS[0] if ARGS else "main_r1"
BLOG = "--blog" in sys.argv
RES = ROOT / "results" / RUN
OUT = ROOT / "report" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
LANG = ["en", "hi", "hg"]
LANG_UP = {"en": "EN", "hi": "HI", "hg": "HG"}
READER = {"llama3.1-8b": "Llama-3.1-8B", "qwen3-8b": "Qwen3-8B"}

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"], "font.size": 8,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlesize": 9, "axes.titlecolor": INK,
    "axes.titleweight": "bold", "xtick.color": INK2, "ytick.color": INK2, "xtick.major.size": 0,
    "ytick.major.size": 0, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "legend.frameon": False, "pdf.fonttype": 42,
})


def save(fig, name):
    if BLOG:
        name += "_blog"
    for ext in (("png",) if BLOG else ("pdf", "png")):
        fig.savefig(OUT / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT / f"{name}.pdf")


# ---------------------------------------------------------------- fig 1: 3x3 heatmaps
d = pd.read_csv(RES / "scored.csv")
A = d[d.answerable]
acc = A.groupby(["model", "setup", "store", "query"]).correct.mean()
cmap = LinearSegmentedColormap.from_list("blue", BLUE)
vmin, vmax = 0.6, 1.0
fig, axes = plt.subplots(1, 4, figsize=(7.0, 2.05), gridspec_kw=dict(wspace=0.25))
for ax, (m, s) in zip(axes, [(m, s) for s in ("FC", "RM-S1") for m in READER]):
    g = np.array([[acc[(m, s, st, q)] for q in LANG] for st in LANG])
    ax.imshow(g, cmap=cmap, vmin=vmin, vmax=vmax)
    for i in range(3):
        for j in range(3):
            v = g[i, j]
            light = (v - vmin) / (vmax - vmin) < 0.55
            ax.text(j, i, f"{100 * v:.0f}", ha="center", va="center", fontsize=8,
                    color=INK if light else "white", fontweight="bold" if i == j else "normal")
    # 2px surface gaps between cells
    for k in (0.5, 1.5):
        ax.axhline(k, color=SURFACE, lw=2)
        ax.axvline(k, color=SURFACE, lw=2)
    ax.set_xticks(range(3), [LANG_UP[l] for l in LANG])
    ax.set_yticks(range(3), [LANG_UP[l] for l in LANG])
    ax.set_title(f"{READER[m]} · {({'FC': 'full context', 'RM-S1': 'retrieval'} if BLOG else {}).get(s, s)}", fontsize=8)
    ax.set_xlabel("question language" if BLOG else "query language")
    for sp in ax.spines.values():
        sp.set_visible(False)
axes[0].set_ylabel("memory language" if BLOG else "storage language")
fig.suptitle("Accuracy (%) by memory language × question language; bold diagonal = same language" if BLOG else
             "Accuracy (%) by storage × query language; diagonal = monolingual (bold)", x=0.5, y=1.05,
             fontsize=9, fontweight="bold", color=INK)
save(fig, "fig1_heatmaps")

# ---------------------------------------------------------------- fig 2: H1 gap with CI
h1 = pd.read_csv(RES / "analysis" / "h1_gap.csv")
SETUPS = ["FC", "RM-S1", "RM-S2", "RM-S3", "OR-S1", "OR-S2", "OR-S3"]
fig, ax = plt.subplots(figsize=(4.6, 2.6) if BLOG else (3.5, 2.3))
ax.axhline(0, color=MUTED, lw=0.8)
for k, (m, col) in enumerate(zip(READER, SERIES)):
    r = h1[h1.model == m].set_index("setup").loc[SETUPS]
    x = np.arange(len(SETUPS)) + (k - 0.5) * 0.24
    ax.vlines(x, 100 * r.ci_lo, 100 * r.ci_hi, color=col, lw=2)
    ax.scatter(x, 100 * r.gap, s=30, color=col, edgecolor=SURFACE, linewidth=1.5, zorder=3, label=READER[m])
BLOG_SETUPS = ["Full\ncontext", "Retrieval\noriginal", "Retrieval\nEnglish", "Retrieval\nboth", "Oracle\noriginal",
               "Oracle\nEnglish", "Oracle\nboth"]
ax.set_xticks(range(len(SETUPS)), BLOG_SETUPS if BLOG else SETUPS, fontsize=6.5 if BLOG else 8)
ax.set_ylim(100 * h1.ci_lo.min() - 1, 100 * h1.ci_hi.max() + 1.5)
ax.set_ylabel("accuracy lost when languages\ndiffer (percentage points)" if BLOG else "mono − cross accuracy (pp)")
ax.yaxis.grid(True, color=GRID, lw=0.6)
ax.set_axisbelow(True)
ax.spines["left"].set_visible(False)
ax.legend(loc="upper right", fontsize=7, handletextpad=0.2)
ax.set_title("How much accuracy drops when languages differ" if BLOG else "Cross-lingual gap (H1), 95% bootstrap CI",
             loc="left")
if BLOG:
    ax.text(0, -0.30, "Dot = measured drop; line = range we are 95% confident it lies in. 0 = no drop.",
            transform=ax.transAxes, fontsize=6.5, color=MUTED)
save(fig, "fig2_h1_gap")

# ---------------------------------------------------------------- fig 3: retrieval recall on cross-lingual cells
rc = pd.read_csv(RES / "analysis" / "h4_recall_cross.csv")
RET = [("bm25", "BM25"), ("bge-m3", "BGE-M3"), ("me5", "mE5")]
assert {k for k, _ in RET} == set(rc.retriever), set(rc.retriever)
STRAT = [("S1", "Original language"), ("S2", "Translated to English"), ("S3", "Both")] if BLOG else \
    [("S1", "S1 original"), ("S2", "S2 English pivot"), ("S3", "S3 dual")]
fig, ax = plt.subplots(figsize=(3.5, 2.3))
w = 0.26
for k, ((s, lab), col) in enumerate(zip(STRAT, SERIES)):
    vals = [100 * rc[(rc.retriever == r) & (rc.strategy == s)]["R@5"].iloc[0] for r, _ in RET]
    x = np.arange(len(RET)) + (k - 1) * w
    ax.bar(x, vals, width=w - 0.03, color=col, label=lab, edgecolor=SURFACE, linewidth=1)
    for xi, v in zip(x, vals):
        ax.text(xi, v + 1.5, f"{v:.0f}", ha="center", va="bottom", fontsize=6.5, color=INK2)
ax.set_xticks(range(len(RET)), ["BM25\n(keyword)", "BGE-M3\n(multilingual)", "mE5\n(multilingual)"] if BLOG else [n for _, n in RET])
ax.set_ylim(0, 112)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_ylabel("right memory in top 5 (%)" if BLOG else "recall@5 (%)")
ax.yaxis.grid(True, color=GRID, lw=0.6)
ax.set_axisbelow(True)
ax.spines["left"].set_visible(False)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.24 if BLOG else -0.14), ncol=3, fontsize=6.5, handlelength=1, columnspacing=0.8)
ax.set_title("Finding the memory when languages differ" if BLOG else "Retrieval on cross-lingual cells", loc="left")
save(fig, "fig3_recall")

# ---------------------------------------------------------------- fig 4: error taxonomy
E = pd.read_csv(RES / "analysis" / "error_taxonomy.csv", keep_default_na=False)
GROUPS = [("False abstention", ["E6"]), ("Distractor capture", ["E4"]),
          ("Wrong entity / number / script", ["E1", "E2", "E5"]), ("Off-task / degenerate", ["E9"]),
          ("Other (unsupported, partial, inversion)", ["E7", "E8", "E3"]), ("Actually correct (judge miss)", ["OK"])]
BLOG_NAMES = ["Says “I don't know”", "Picks the decoy fact", "Wrong name, number or script", "Rambles / off-task",
              "Other", "Actually correct (judge was wrong)"]
code2g = {c: g for g, cs in GROUPS for c in cs}
E["g"] = E.final.map(code2g)
rows = [("Same language" if BLOG else "Monolingual", E.cell == "mono"),
        ("Different languages" if BLOG else "Cross-lingual", E.cell == "cross"),
        ("Full context", E.grp == "FC"), ("Retrieval", E.grp == "RM"), ("Oracle", E.grp == "OR")]
fig, ax = plt.subplots(figsize=(7.0, 1.9))
for i, (lab, mask) in enumerate(rows):
    sub = E[mask]
    share = sub.groupby("g").weight.sum() / sub.weight.sum()
    left = 0.0
    for (g, _), col in zip(GROUPS, SERIES):
        v = 100 * share.get(g, 0.0)
        ax.barh(i, v, left=left, height=0.62, color=col, edgecolor=SURFACE, linewidth=1.5)
        if v >= (5 if BLOG else 7):
            ax.text(left + v / 2, i, f"{v:.0f}", ha="center", va="center", fontsize=6.5,
                    color="white" if col in (SERIES[0], SERIES[1], SERIES[5]) else INK)
        left += v
    if not BLOG:
        ax.text(101, i, f"n={mask.sum()}", va="center", fontsize=6.5, color=MUTED)
ax.set_yticks(range(len(rows)), [r[0] for r in rows])
ax.invert_yaxis()
ax.axhline(1.5, color=GRID, lw=0.8)
ax.set_xlim(0, 100)
ax.set_xticks([0, 25, 50, 75, 100], ["0", "25", "50", "75", "100%"])
for sp in ("left", "bottom"):
    ax.spines[sp].set_visible(False)
ax.legend(handles=[Patch(color=c, label=b if BLOG else g) for (g, _), c, b in zip(GROUPS, SERIES, BLOG_NAMES)],
          loc="lower center",
          bbox_to_anchor=(0.45, 1.0), ncol=3, fontsize=6.5, handlelength=1, columnspacing=1.2)
ax.set_title("What kind of mistakes the models make (% of errors)" if BLOG else
             "Error types in 150 sampled errors (weighted to all 2,386 errors)", loc="left", pad=34)
save(fig, "fig4_errors")
