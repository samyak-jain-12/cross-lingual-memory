"""Method overview diagram for the paper (static PDF/PNG).

Run from the project root:  python src/make_method_figure.py
Writes report/paper/figures/fig0_method_overview.{pdf,png}
Coordinates are in inches (axes scaled 1:1), so squares stay square.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
BLUE, BLUE_L, ORANGE_L = "#2a78d6", "#e6f0fb", "#fdeee7"
INK, INK2, EDGE, GREY_L = "#0b0b0b", "#52514e", "#bdbcb6", "#f3f2ef"
W, H = 7.0, 2.3
plt.rcParams.update({"font.family": "DejaVu Sans"})


def box(ax, x, y, w, h, title, lines, fill=GREY_L, edge=EDGE):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.06", fc=fill, ec=edge, lw=0.9))
    ax.text(x + w / 2, y + h - 0.13, title, ha="center", va="center", fontsize=7.6, fontweight="bold", color=INK)
    ax.text(x + w / 2, y + h - 0.27, "\n".join(lines), ha="center", va="top", fontsize=6.5, color=INK2, linespacing=1.35)


def arrow(ax, p0, p1):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=8, lw=0.9, color=INK2, shrinkA=0, shrinkB=0))


fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")

top, bot = 2.15, 0.12          # vertical extent of the main boxes
mid = (top + bot) / 2

# 1. Fixed memory
box(ax, 0.05, bot, 1.12, top - bot, "1. Fixed memory",
    ["one fact, preference", "or event the user", "told the assistant", "", "written in", "EN  English", "HI  Hindi",
     "HG  Hinglish", "", "same answer", "in all three"])

# 2. Storage x question grid (square cells)
cs, gx, gy = 0.27, 1.62, 0.62
ax.text(gx + 1.5 * cs, top - 0.13, "2. Storage × question", ha="center", va="center", fontsize=7.6,
        fontweight="bold", color=INK)
ax.text(gx + 1.5 * cs, gy + 3 * cs + 0.27, "question language", ha="center", fontsize=6.3, color=INK2)
for j, l in enumerate(("EN", "HI", "HG")):
    ax.text(gx + (j + 0.5) * cs, gy + 3 * cs + 0.08, l, ha="center", fontsize=6.3, color=INK2)
for i, s in enumerate(("EN", "HI", "HG")):
    ax.text(gx - 0.06, gy + (2.5 - i) * cs, s, ha="right", va="center", fontsize=6.3, color=INK2)
    for j in range(3):
        ax.add_patch(FancyBboxPatch((gx + j * cs + 0.02, gy + (2 - i) * cs + 0.02), cs - 0.04, cs - 0.04,
                                    boxstyle="round,pad=0,rounding_size=0.03",
                                    fc=BLUE if i == j else ORANGE_L, ec="none"))
ax.text(gx - 0.36, gy + 1.5 * cs, "storage", rotation=90, ha="center", va="center", fontsize=6.3, color=INK2)
ax.text(gx + 1.5 * cs, gy - 0.12, "blue: same language\npeach: cross-lingual", ha="center", va="top",
        fontsize=6.2, color=INK2, linespacing=1.3)

# 3. History in storage language
box(ax, 2.70, bot, 1.18, top - bot, "3. History in s",
    ["10 sessions, all in", "storage language s", "", "1 memory session", "9 filler sessions", "1 distractor (30%)",
     "", "same layout in", "every language"])

# 4. Memory setups
sx, sw = 4.08, 1.42
ax.text(sx + sw / 2, top - 0.02, "4. Memory setup", ha="center", va="center", fontsize=7.6, fontweight="bold", color=INK)
setups = [(1.38, 0.55, "Full context (FC)", ["whole history in prompt"]),
          (0.70, 0.62, "Retrieval (RM)", ["top-5 turns stored as", "S1 orig | S2 Eng | S3 both"]),
          (0.12, 0.52, "Oracle (OR)", ["only the gold turn"])]
for y, h, t, lines in setups:
    box(ax, sx, y, sw, h, t, lines, fill=BLUE_L, edge=BLUE)

# 5. Reader, 6. Evaluation
box(ax, 5.72, 1.17, 1.23, top - 1.17, "5. Reader LLM", ["Qwen3-8B or", "Llama-3.1-8B", "answers question", "in language ℓ"])
box(ax, 5.72, bot, 1.23, 0.88, "6. Evaluation", ["LLM judge, slot match", "Recall@k", "RM vs OR: retrieval", "or reading error"])

# Arrows
arrow(ax, (1.18, 1.72), (1.30, 1.72))   # above the rotated "storage" label
arrow(ax, (2.50, mid), (2.69, mid))
for y, h, *_ in setups:
    arrow(ax, (3.89, mid), (sx - 0.01, y + h / 2))
    arrow(ax, (sx + sw + 0.01, y + h / 2), (5.71, 1.17 + (top - 1.17) / 2))
arrow(ax, (6.335, 1.16), (6.335, bot + 0.89))

out = ROOT / "report" / "paper" / "figures"
out.mkdir(parents=True, exist_ok=True)
for ext in ("pdf", "png"):
    fig.savefig(out / f"fig0_method_overview.{ext}", dpi=300, bbox_inches="tight", pad_inches=0.03)
print("wrote", out / "fig0_method_overview.pdf")
