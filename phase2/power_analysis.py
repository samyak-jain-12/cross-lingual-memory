"""Power of the exact McNemar test for a paired accuracy gap between two conditions.

Each item is answered under condition A and condition B. Only discordant items
(right in one, wrong in the other) carry information. We simulate n items with a
given discordant rate and true gap `delta` = P(A right, B wrong) - P(A wrong, B right).

Run: python phase2/power_analysis.py   (needs numpy, scipy)
"""
import numpy as np
from scipy.stats import binomtest

rng = np.random.default_rng(0)


def power(n, delta, disc, sims=3000, alpha=0.05):
    p10, p01 = (disc + delta) / 2, (disc - delta) / 2
    hits = 0
    for _ in range(sims):
        b, c, _ = rng.multinomial(n, [p10, p01, 1 - p10 - p01])
        if b + c and binomtest(b, b + c, 0.5).pvalue < alpha:
            hits += 1
    return hits / sims


if __name__ == "__main__":
    gaps = [0.05, 0.08, 0.10, 0.12, 0.15]
    for n in [100, 150, 200]:
        for disc in [0.15, 0.25, 0.35]:
            row = " ".join(f"{power(n, g, disc):.2f}" for g in gaps)
            print(f"n={n:3d} discordant={disc:.2f} | gaps 5/8/10/12/15pp -> {row}")
