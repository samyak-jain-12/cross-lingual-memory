# Analysis of `main_r1` (pre-registered tests, design_spec §1)

Answerable items: 150 · controls: 15 · readers: llama3.1-8b, qwen3-8b
Item accuracy in a condition = mean over its cells × paraphrases. α = .05 two-sided, Holm within each family.

## H1: cross-lingual cells score lower than monolingual cells

Gap = mono − cross, item-paired; 95% bootstrap CI; paired permutation test (10k); Holm over the 7 setups per reader.
Noise floors on monolingual cells: *disagree* = P(q1 ≠ q2) per observation (the spec's rule; every gap here is below it, but it is a per-answer flip rate, not a difference in means); *para* = |acc(q1) − acc(q2)| item-paired, with the outer edge of its 95% CI. A gap 'beats paraphrase noise' when its CI lower bound is above that edge (DEVIATIONS #13).

| model | setup | mono | cross | gap | CI | p | verdict | disagree | para | beats_para |
|---|---|---|---|---|---|---|---|---|---|---|
| llama3.1-8b | FC | 85.0% | 77.1% | +7.9pp | [+5.3, +10.6] | <.001 | supported | 17.6% | 4.2 (≤8.7) | no |
| llama3.1-8b | RM-S1 | 97.2% | 95.4% | +1.8pp | [+0.8, +2.9] | 0.004 | supported | 4.2% | 2.9 (≤5.6) | no |
| llama3.1-8b | RM-S2 | 96.2% | 96.4% | -0.2pp | [-1.4, +1.1] | 0.862 | not significant | 5.8% | 1.8 (≤4.4) | no |
| llama3.1-8b | RM-S3 | 97.9% | 96.1% | +1.8pp | [+0.7, +2.9] | 0.004 | supported | 4.2% | 3.3 (≤6.0) | no |
| llama3.1-8b | OR-S1 | 98.3% | 97.6% | +0.7pp | [-0.2, +1.7] | 0.550 | not significant | 2.0% | 0.7 (≤2.2) | no |
| llama3.1-8b | OR-S2 | 98.3% | 97.7% | +0.7pp | [-0.2, +1.6] | 0.550 | not significant | 2.0% | 0.2 (≤1.6) | no |
| llama3.1-8b | OR-S3 | 98.8% | 98.0% | +0.8pp | [-0.2, +1.7] | 0.550 | not significant | 1.6% | 1.1 (≤2.7) | no |
| qwen3-8b | FC | 84.3% | 80.2% | +4.2pp | [+1.9, +6.5] | 0.004 | supported | 15.8% | 5.1 (≤9.6) | no |
| qwen3-8b | RM-S1 | 95.2% | 92.7% | +2.6pp | [+1.2, +3.9] | 0.001 | supported | 5.6% | 3.3 (≤6.4) | no |
| qwen3-8b | RM-S2 | 94.1% | 93.5% | +0.6pp | [-0.7, +1.9] | 0.788 | not significant | 9.1% | 2.4 (≤5.8) | no |
| qwen3-8b | RM-S3 | 95.3% | 93.9% | +1.4pp | [+0.1, +2.7] | 0.141 | not significant | 5.8% | 3.1 (≤6.0) | no |
| qwen3-8b | OR-S1 | 97.0% | 95.1% | +1.9pp | [+0.6, +3.2] | 0.021 | supported | 3.8% | 0.2 (≤2.2) | no |
| qwen3-8b | OR-S2 | 94.2% | 93.9% | +0.3pp | [-0.6, +1.3] | 0.788 | not significant | 7.6% | 0.4 (≤3.1) | no |
| qwen3-8b | OR-S3 | 97.6% | 95.2% | +2.4pp | [+1.2, +3.7] | <.001 | supported | 4.0% | 0.9 (≤3.1) | no |

**Second clause (drop larger for retrieval than full context):** gap(RM-S1) − gap(FC), item-paired, Holm over readers.

- llama3.1-8b: -6.1pp [-8.8, -3.4], p_holm = <.001
- qwen3-8b: -1.6pp [-4.1, +0.9], p_holm = 0.230

## H2: X→EN beats EN→X (mirrored directions)

Exact McNemar on items (wins = items better in A / better in B); Holm over the 3 pairs within reader × setup. (The Kaggle `table_mirror.csv` applied Holm over all 42 tests; this table follows the spec.)

| model | setup | A | B | acc_A | acc_B | diff | CI | wins | p | sig |
|---|---|---|---|---|---|---|---|---|---|---|
| llama3.1-8b | FC | hi→en | en→hi | 82.3% | 69.0% | +13.3pp | [+7.3, +19.3] | 46/13 | <.001 | ✓ |
| llama3.1-8b | FC | hg→en | en→hg | 88.3% | 72.7% | +15.7pp | [+10.0, +21.7] | 45/9 | <.001 | ✓ |
| llama3.1-8b | FC | hg→hi | hi→hg | 83.0% | 67.0% | +16.0pp | [+10.0, +22.3] | 48/13 | <.001 | ✓ |
| llama3.1-8b | RM-S1 | hi→en | en→hi | 98.7% | 95.7% | +3.0pp | [+0.7, +5.7] | 9/2 | 0.131 |  |
| llama3.1-8b | RM-S1 | hg→en | en→hg | 95.3% | 95.3% | +0.0pp | [-2.7, +2.7] | 8/7 | 1.000 |  |
| llama3.1-8b | RM-S1 | hg→hi | hi→hg | 96.0% | 91.3% | +4.7pp | [+0.7, +8.7] | 17/6 | 0.104 |  |
| llama3.1-8b | RM-S2 | hi→en | en→hi | 96.3% | 97.3% | -1.0pp | [-4.3, +2.0] | 7/6 | 1.000 |  |
| llama3.1-8b | RM-S2 | hg→en | en→hg | 97.0% | 96.0% | +1.0pp | [-2.3, +4.3] | 9/4 | 0.801 |  |
| llama3.1-8b | RM-S2 | hg→hi | hi→hg | 95.7% | 96.0% | -0.3pp | [-3.3, +2.7] | 7/7 | 1.000 |  |
| llama3.1-8b | RM-S3 | hi→en | en→hi | 97.3% | 95.7% | +1.7pp | [-1.0, +4.7] | 9/4 | 0.430 |  |
| llama3.1-8b | RM-S3 | hg→en | en→hg | 97.3% | 95.3% | +2.0pp | [-0.3, +4.3] | 10/4 | 0.430 |  |
| llama3.1-8b | RM-S3 | hg→hi | hi→hg | 97.0% | 94.0% | +3.0pp | [-0.3, +6.7] | 12/5 | 0.430 |  |
| llama3.1-8b | OR-S1 | hi→en | en→hi | 98.7% | 98.3% | +0.3pp | [-1.7, +2.3] | 4/2 | 1.000 |  |
| llama3.1-8b | OR-S1 | hg→en | en→hg | 98.0% | 98.3% | -0.3pp | [-2.3, +1.7] | 4/5 | 1.000 |  |
| llama3.1-8b | OR-S1 | hg→hi | hi→hg | 97.0% | 95.3% | +1.7pp | [-1.3, +5.0] | 10/7 | 1.000 |  |
| llama3.1-8b | OR-S2 | hi→en | en→hi | 97.0% | 98.3% | -1.3pp | [-4.7, +1.3] | 5/5 | 1.000 |  |
| llama3.1-8b | OR-S2 | hg→en | en→hg | 97.3% | 98.3% | -1.0pp | [-4.0, +1.7] | 5/5 | 1.000 |  |
| llama3.1-8b | OR-S2 | hg→hi | hi→hg | 98.0% | 97.0% | +1.0pp | [-1.7, +4.0] | 5/5 | 1.000 |  |
| llama3.1-8b | OR-S3 | hi→en | en→hi | 98.3% | 98.3% | +0.0pp | [-2.3, +2.3] | 5/4 | 1.000 |  |
| llama3.1-8b | OR-S3 | hg→en | en→hg | 98.0% | 98.3% | -0.3pp | [-2.3, +1.7] | 4/5 | 1.000 |  |
| llama3.1-8b | OR-S3 | hg→hi | hi→hg | 98.7% | 96.3% | +2.3pp | [+0.0, +5.0] | 7/2 | 0.539 |  |
| qwen3-8b | FC | hi→en | en→hi | 84.3% | 78.0% | +6.3pp | [+1.0, +11.7] | 33/17 | 0.066 |  |
| qwen3-8b | FC | hg→en | en→hg | 91.3% | 65.0% | +26.3pp | [+21.0, +32.0] | 69/2 | <.001 | ✓ |
| qwen3-8b | FC | hg→hi | hi→hg | 82.0% | 80.3% | +1.7pp | [-3.0, +6.3] | 21/16 | 0.511 |  |
| qwen3-8b | RM-S1 | hi→en | en→hi | 93.0% | 91.0% | +2.0pp | [-2.3, +6.3] | 15/10 | 0.849 |  |
| qwen3-8b | RM-S1 | hg→en | en→hg | 95.7% | 91.0% | +4.7pp | [+1.3, +8.3] | 19/5 | 0.020 | ✓ |
| qwen3-8b | RM-S1 | hg→hi | hi→hg | 92.0% | 93.3% | -1.3pp | [-4.3, +1.7] | 6/10 | 0.849 |  |
| qwen3-8b | RM-S2 | hi→en | en→hi | 93.7% | 92.7% | +1.0pp | [-3.0, +5.0] | 14/10 | 0.541 |  |
| qwen3-8b | RM-S2 | hg→en | en→hg | 96.3% | 92.7% | +3.7pp | [+0.3, +7.0] | 17/5 | 0.051 |  |
| qwen3-8b | RM-S2 | hg→hi | hi→hg | 94.3% | 91.3% | +3.0pp | [-1.0, +7.0] | 19/11 | 0.401 |  |
| qwen3-8b | RM-S3 | hi→en | en→hi | 94.7% | 91.0% | +3.7pp | [-0.3, +8.0] | 16/7 | 0.186 |  |
| qwen3-8b | RM-S3 | hg→en | en→hg | 97.3% | 91.0% | +6.3pp | [+3.7, +9.3] | 20/1 | <.001 | ✓ |
| qwen3-8b | RM-S3 | hg→hi | hi→hg | 95.3% | 94.3% | +1.0pp | [-1.3, +3.7] | 7/5 | 0.774 |  |
| qwen3-8b | OR-S1 | hi→en | en→hi | 97.3% | 93.3% | +4.0pp | [+0.7, +7.3] | 15/4 | 0.038 | ✓ |
| qwen3-8b | OR-S1 | hg→en | en→hg | 96.7% | 92.3% | +4.3pp | [+1.3, +7.3] | 18/5 | 0.032 | ✓ |
| qwen3-8b | OR-S1 | hg→hi | hi→hg | 94.7% | 96.3% | -1.7pp | [-4.3, +0.7] | 3/6 | 0.508 |  |
| qwen3-8b | OR-S2 | hi→en | en→hi | 94.7% | 93.3% | +1.3pp | [-2.3, +5.0] | 15/8 | 0.244 |  |
| qwen3-8b | OR-S2 | hg→en | en→hg | 97.0% | 92.3% | +4.7pp | [+1.3, +8.0] | 19/4 | 0.008 | ✓ |
| qwen3-8b | OR-S2 | hg→hi | hi→hg | 94.7% | 91.3% | +3.3pp | [-0.7, +7.7] | 18/9 | 0.244 |  |
| qwen3-8b | OR-S3 | hi→en | en→hi | 95.7% | 93.3% | +2.3pp | [-1.3, +6.0] | 15/7 | 0.237 |  |
| qwen3-8b | OR-S3 | hg→en | en→hg | 98.0% | 92.3% | +5.7pp | [+3.0, +8.7] | 19/2 | <.001 | ✓ |
| qwen3-8b | OR-S3 | hg→hi | hi→hg | 97.3% | 94.3% | +3.0pp | [+0.3, +6.0] | 11/4 | 0.237 |  |

## H3: Hinglish queries vs Devanagari Hindi queries (two-sided)

Pairs from the spec: EN→HG vs EN→HI, HI→HG vs HI→HI, HG→HG vs HI→HI. Exact McNemar on items, Holm within reader × setup.

| model | setup | A | B | acc_A | acc_B | diff | CI | wins | p | sig |
|---|---|---|---|---|---|---|---|---|---|---|
| llama3.1-8b | FC | en→hg | en→hi | 72.7% | 69.0% | +3.7pp | [-4.3, +11.3] | 41/31 | 0.578 |  |
| llama3.1-8b | FC | hi→hg | hi→hi | 67.0% | 82.7% | -15.7pp | [-22.3, -9.0] | 12/48 | <.001 | ✓ |
| llama3.1-8b | FC | hg→hg | hi→hi | 85.7% | 82.7% | +3.0pp | [-2.3, +8.7] | 25/21 | 0.659 |  |
| llama3.1-8b | RM-S1 | en→hg | en→hi | 95.3% | 95.7% | -0.3pp | [-3.3, +2.7] | 10/10 | 1.000 |  |
| llama3.1-8b | RM-S1 | hi→hg | hi→hi | 91.3% | 96.3% | -5.0pp | [-8.3, -2.3] | 2/15 | 0.007 | ✓ |
| llama3.1-8b | RM-S1 | hg→hg | hi→hi | 97.0% | 96.3% | +0.7pp | [-2.0, +3.3] | 6/6 | 1.000 |  |
| llama3.1-8b | RM-S2 | en→hg | en→hi | 96.0% | 97.3% | -1.3pp | [-3.3, +0.7] | 3/7 | 1.000 |  |
| llama3.1-8b | RM-S2 | hi→hg | hi→hi | 96.0% | 95.3% | +0.7pp | [-2.0, +3.3] | 8/7 | 1.000 |  |
| llama3.1-8b | RM-S2 | hg→hg | hi→hi | 95.0% | 95.3% | -0.3pp | [-3.3, +2.7] | 8/10 | 1.000 |  |
| llama3.1-8b | RM-S3 | en→hg | en→hi | 95.3% | 95.7% | -0.3pp | [-3.7, +2.7] | 10/10 | 1.000 |  |
| llama3.1-8b | RM-S3 | hi→hg | hi→hi | 94.0% | 97.7% | -3.7pp | [-7.0, -0.7] | 3/11 | 0.172 |  |
| llama3.1-8b | RM-S3 | hg→hg | hi→hi | 97.7% | 97.7% | +0.0pp | [-2.0, +1.7] | 4/4 | 1.000 |  |
| llama3.1-8b | OR-S1 | en→hg | en→hi | 98.3% | 98.3% | +0.0pp | [-2.0, +2.0] | 5/5 | 1.000 |  |
| llama3.1-8b | OR-S1 | hi→hg | hi→hi | 95.3% | 97.3% | -2.0pp | [-4.3, +0.3] | 3/9 | 0.438 |  |
| llama3.1-8b | OR-S1 | hg→hg | hi→hi | 97.7% | 97.3% | +0.3pp | [-2.3, +2.7] | 5/4 | 1.000 |  |
| llama3.1-8b | OR-S2 | en→hg | en→hi | 98.3% | 98.3% | +0.0pp | [-2.0, +2.0] | 5/5 | 1.000 |  |
| llama3.1-8b | OR-S2 | hi→hg | hi→hi | 97.0% | 98.0% | -1.0pp | [-3.3, +1.3] | 3/4 | 1.000 |  |
| llama3.1-8b | OR-S2 | hg→hg | hi→hi | 97.0% | 98.0% | -1.0pp | [-3.7, +1.7] | 4/7 | 1.000 |  |
| llama3.1-8b | OR-S3 | en→hg | en→hi | 98.3% | 98.3% | +0.0pp | [-2.0, +2.0] | 5/5 | 1.000 |  |
| llama3.1-8b | OR-S3 | hi→hg | hi→hi | 96.3% | 97.3% | -1.0pp | [-4.0, +2.0] | 3/7 | 1.000 |  |
| llama3.1-8b | OR-S3 | hg→hg | hi→hi | 99.0% | 97.3% | +1.7pp | [-0.3, +4.0] | 4/1 | 1.000 |  |
| qwen3-8b | FC | en→hg | en→hi | 65.0% | 78.0% | -13.0pp | [-19.7, -6.7] | 21/55 | <.001 | ✓ |
| qwen3-8b | FC | hi→hg | hi→hi | 80.3% | 83.0% | -2.7pp | [-7.0, +1.3] | 14/21 | 0.311 |  |
| qwen3-8b | FC | hg→hg | hi→hi | 78.7% | 83.0% | -4.3pp | [-9.3, +1.0] | 17/28 | 0.270 |  |
| qwen3-8b | RM-S1 | en→hg | en→hi | 91.0% | 91.0% | +0.0pp | [-4.0, +4.0] | 15/16 | 1.000 |  |
| qwen3-8b | RM-S1 | hi→hg | hi→hi | 93.3% | 95.0% | -1.7pp | [-3.3, +0.0] | 1/6 | 0.375 |  |
| qwen3-8b | RM-S1 | hg→hg | hi→hi | 94.3% | 95.0% | -0.7pp | [-3.7, +2.0] | 6/6 | 1.000 |  |
| qwen3-8b | RM-S2 | en→hg | en→hi | 92.7% | 92.7% | +0.0pp | [-3.0, +3.3] | 10/11 | 1.000 |  |
| qwen3-8b | RM-S2 | hi→hg | hi→hi | 91.3% | 91.7% | -0.3pp | [-4.0, +3.3] | 14/13 | 1.000 |  |
| qwen3-8b | RM-S2 | hg→hg | hi→hi | 94.3% | 91.7% | +2.7pp | [-1.0, +6.7] | 17/11 | 1.000 |  |
| qwen3-8b | RM-S3 | en→hg | en→hi | 91.0% | 91.0% | +0.0pp | [-4.0, +4.3] | 15/16 | 1.000 |  |
| qwen3-8b | RM-S3 | hi→hg | hi→hi | 94.3% | 95.7% | -1.3pp | [-4.0, +1.0] | 5/8 | 1.000 |  |
| qwen3-8b | RM-S3 | hg→hg | hi→hi | 94.0% | 95.7% | -1.7pp | [-4.7, +1.0] | 6/10 | 1.000 |  |
| qwen3-8b | OR-S1 | en→hg | en→hi | 92.3% | 93.3% | -1.0pp | [-4.7, +2.7] | 15/18 | 1.000 |  |
| qwen3-8b | OR-S1 | hi→hg | hi→hi | 96.3% | 96.3% | +0.0pp | [-2.0, +2.0] | 5/5 | 1.000 |  |
| qwen3-8b | OR-S1 | hg→hg | hi→hi | 96.7% | 96.3% | +0.3pp | [-2.3, +3.0] | 6/5 | 1.000 |  |
| qwen3-8b | OR-S2 | en→hg | en→hi | 92.3% | 93.3% | -1.0pp | [-4.7, +2.7] | 15/18 | 1.000 |  |
| qwen3-8b | OR-S2 | hi→hg | hi→hi | 91.3% | 90.3% | +1.0pp | [-3.0, +5.0] | 16/13 | 1.000 |  |
| qwen3-8b | OR-S2 | hg→hg | hi→hi | 94.3% | 90.3% | +4.0pp | [-0.3, +8.3] | 19/9 | 0.261 |  |
| qwen3-8b | OR-S3 | en→hg | en→hi | 92.3% | 93.3% | -1.0pp | [-4.7, +2.7] | 15/18 | 1.000 |  |
| qwen3-8b | OR-S3 | hi→hg | hi→hi | 94.3% | 97.0% | -2.7pp | [-5.7, +0.0] | 4/10 | 0.539 |  |
| qwen3-8b | OR-S3 | hg→hg | hi→hi | 97.7% | 97.0% | +0.7pp | [-1.7, +3.0] | 7/5 | 1.000 |  |

## H4: memory representation on cross-lingual cells (S3 dual ≥ S2 pivot > S1 original)

Accuracy pooled over the 6 cross-lingual cells. Cochran's Q on (item × cell × paraphrase) units as in the spec; Friedman on item means as a clustering-robust check; pairwise exact McNemar on items with Holm (3 pairs).

| model | group | S1 | S2 | S3 | Q | p_Q | p_Friedman |
|---|---|---|---|---|---|---|---|
| llama3.1-8b | RM | 95.4% | 96.4% | 96.1% | 4.4 | 0.111 | 0.188 |
| llama3.1-8b | OR | 97.6% | 97.7% | 98.0% | 1.3 | 0.521 | 0.381 |
| qwen3-8b | RM | 92.7% | 93.5% | 93.9% | 6.5 | 0.039 | 0.229 |
| qwen3-8b | OR | 95.1% | 93.9% | 95.2% | 10.7 | 0.005 | 0.069 |

| model | A | B | diff | CI | wins | p | sig |
|---|---|---|---|---|---|---|---|
| llama3.1-8b | RM-S3 | RM-S1 | +0.7pp | [-0.2, +1.7] | 17/7 | 0.192 |  |
| llama3.1-8b | RM-S2 | RM-S1 | +1.0pp | [-0.7, +2.7] | 24/16 | 0.536 |  |
| llama3.1-8b | RM-S3 | RM-S2 | -0.3pp | [-2.1, +1.3] | 18/20 | 0.871 |  |
| llama3.1-8b | OR-S3 | OR-S1 | +0.4pp | [-0.4, +1.2] | 14/10 | 1.000 |  |
| llama3.1-8b | OR-S2 | OR-S1 | +0.1pp | [-1.3, +1.3] | 19/12 | 0.843 |  |
| llama3.1-8b | OR-S3 | OR-S2 | +0.3pp | [-0.6, +1.4] | 10/13 | 1.000 |  |
| qwen3-8b | RM-S3 | RM-S1 | +1.3pp | [+0.4, +2.3] | 18/8 | 0.227 |  |
| qwen3-8b | RM-S2 | RM-S1 | +0.8pp | [-0.6, +2.3] | 31/24 | 0.838 |  |
| qwen3-8b | RM-S3 | RM-S2 | +0.4pp | [-0.7, +1.6] | 26/20 | 0.838 |  |
| qwen3-8b | OR-S3 | OR-S1 | +0.1pp | [-0.9, +1.1] | 17/15 | 0.860 |  |
| qwen3-8b | OR-S2 | OR-S1 | -1.2pp | [-2.6, +0.1] | 12/27 | 0.071 |  |
| qwen3-8b | OR-S3 | OR-S2 | +1.3pp | [+0.3, +2.4] | 25/16 | 0.422 |  |

Recall on cross-lingual cells (mean over the 6 cells):

| retriever | strategy | R@1 | R@5 |
|---|---|---|---|
| bge-m3 | S1 | 86.8% | 98.4% |
| bge-m3 | S2 | 91.8% | 99.7% |
| bge-m3 | S3 | 88.1% | 98.9% |
| bm25 | S1 | 41.6% | 45.7% |
| bm25 | S2 | 83.1% | 93.3% |
| bm25 | S3 | 62.6% | 69.6% |
| me5 | S1 | 86.6% | 98.6% |
| me5 | S2 | 94.9% | 99.9% |
| me5 | S3 | 87.8% | 98.7% |

S2 pivot minus S1 original on cross-lingual cells, by gold slot kind (tests 'S2 loses on names and numbers'):

| model | slot_kind | items | S1 | S2 | diff | CI | p |
|---|---|---|---|---|---|---|---|
| llama3.1-8b | number/date | 77 | 98.2% | 98.3% | +0.1pp | [-1.7, +1.7] | 0.508 |
| llama3.1-8b | name/other | 73 | 92.5% | 94.4% | +1.9pp | [-0.9, +5.0] | 0.473 |
| qwen3-8b | number/date | 77 | 97.0% | 97.3% | +0.3pp | [-1.6, +2.4] | 1.000 |
| qwen3-8b | name/other | 73 | 88.1% | 89.5% | +1.4pp | [-0.8, +3.5] | 0.405 |

## Diagnostic: retrieval vs reading

Mean over cells (mono = 3 diagonal, cross = 6 off-diagonal); from `table_stages.csv`.

| model | strategy | cell | retrieval_miss | reading_error_given_hit | oracle_error | end_to_end_error |
|---|---|---|---|---|---|---|
| llama3.1-8b | S1 | cross | 1.6% | 3.1% | 2.4% | 4.6% |
| llama3.1-8b | S1 | mono | 0.8% | 2.0% | 1.7% | 2.8% |
| llama3.1-8b | S2 | cross | 0.3% | 3.3% | 2.3% | 3.6% |
| llama3.1-8b | S2 | mono | 0.4% | 3.4% | 1.7% | 3.8% |
| llama3.1-8b | S3 | cross | 1.1% | 2.8% | 2.0% | 3.9% |
| llama3.1-8b | S3 | mono | 0.8% | 1.3% | 1.2% | 2.1% |
| qwen3-8b | S1 | cross | 1.6% | 5.9% | 4.9% | 7.3% |
| qwen3-8b | S1 | mono | 0.8% | 4.0% | 3.0% | 4.8% |
| qwen3-8b | S2 | cross | 0.3% | 6.2% | 6.1% | 6.5% |
| qwen3-8b | S2 | mono | 0.4% | 5.5% | 5.8% | 5.9% |
| qwen3-8b | S3 | cross | 1.1% | 5.0% | 4.8% | 6.1% |
| qwen3-8b | S3 | mono | 0.8% | 3.9% | 2.4% | 4.7% |

## Breakdowns (descriptive): memory type, evidence position, distractor

| model | setup | factor | level | items | mono | cross | gap |
|---|---|---|---|---|---|---|---|
| llama3.1-8b | FC | memory_type | event | 50 | 93.0% | 84.5% | +8.5pp |
| llama3.1-8b | FC | memory_type | fact | 50 | 80.7% | 72.5% | +8.2pp |
| llama3.1-8b | FC | memory_type | preference | 50 | 81.3% | 74.2% | +7.2pp |
| llama3.1-8b | FC | evidence_class | early | 51 | 82.0% | 73.5% | +8.5pp |
| llama3.1-8b | FC | evidence_class | late | 48 | 90.3% | 83.9% | +6.4pp |
| llama3.1-8b | FC | evidence_class | middle | 51 | 83.0% | 74.2% | +8.8pp |
| llama3.1-8b | FC | has_distractor | False | 75 | 87.6% | 79.2% | +8.3pp |
| llama3.1-8b | FC | has_distractor | True | 75 | 82.4% | 74.9% | +7.6pp |
| llama3.1-8b | RM-S1 | memory_type | event | 50 | 99.3% | 98.5% | +0.8pp |
| llama3.1-8b | RM-S1 | memory_type | fact | 50 | 96.0% | 94.0% | +2.0pp |
| llama3.1-8b | RM-S1 | memory_type | preference | 50 | 96.3% | 93.7% | +2.7pp |
| llama3.1-8b | RM-S1 | evidence_class | early | 51 | 96.7% | 94.8% | +2.0pp |
| llama3.1-8b | RM-S1 | evidence_class | late | 48 | 98.6% | 98.1% | +0.5pp |
| llama3.1-8b | RM-S1 | evidence_class | middle | 51 | 96.4% | 93.5% | +2.9pp |
| llama3.1-8b | RM-S1 | has_distractor | False | 75 | 98.0% | 96.6% | +1.4pp |
| llama3.1-8b | RM-S1 | has_distractor | True | 75 | 96.4% | 94.2% | +2.2pp |
| qwen3-8b | FC | memory_type | event | 50 | 96.0% | 90.3% | +5.7pp |
| qwen3-8b | FC | memory_type | fact | 50 | 85.3% | 80.0% | +5.3pp |
| qwen3-8b | FC | memory_type | preference | 50 | 71.7% | 70.2% | +1.5pp |
| qwen3-8b | FC | evidence_class | early | 51 | 81.7% | 76.5% | +5.2pp |
| qwen3-8b | FC | evidence_class | late | 48 | 92.0% | 92.0% | +0.0pp |
| qwen3-8b | FC | evidence_class | middle | 51 | 79.7% | 72.7% | +7.0pp |
| qwen3-8b | FC | has_distractor | False | 75 | 86.4% | 80.4% | +6.0pp |
| qwen3-8b | FC | has_distractor | True | 75 | 82.2% | 79.9% | +2.3pp |
| qwen3-8b | RM-S1 | memory_type | event | 50 | 98.7% | 97.2% | +1.5pp |
| qwen3-8b | RM-S1 | memory_type | fact | 50 | 95.0% | 91.0% | +4.0pp |
| qwen3-8b | RM-S1 | memory_type | preference | 50 | 92.0% | 89.8% | +2.2pp |
| qwen3-8b | RM-S1 | evidence_class | early | 51 | 93.8% | 92.0% | +1.8pp |
| qwen3-8b | RM-S1 | evidence_class | late | 48 | 99.7% | 97.6% | +2.1pp |
| qwen3-8b | RM-S1 | evidence_class | middle | 51 | 92.5% | 88.7% | +3.8pp |
| qwen3-8b | RM-S1 | has_distractor | False | 75 | 96.4% | 93.7% | +2.8pp |
| qwen3-8b | RM-S1 | has_distractor | True | 75 | 94.0% | 91.7% | +2.3pp |

False abstention on answerable items (share of answers that say 'I don't know'):

| model | setup | mono | cross |
|---|---|---|---|
| llama3.1-8b | FC | 6.2% | 11.2% |
| llama3.1-8b | OR-S1 | 0.2% | 0.7% |
| llama3.1-8b | OR-S2 | 0.2% | 0.7% |
| llama3.1-8b | OR-S3 | 0.2% | 0.4% |
| llama3.1-8b | RM-S1 | 0.9% | 1.7% |
| llama3.1-8b | RM-S2 | 0.7% | 1.3% |
| llama3.1-8b | RM-S3 | 0.9% | 1.2% |
| qwen3-8b | FC | 6.1% | 8.7% |
| qwen3-8b | OR-S1 | 0.3% | 0.6% |
| qwen3-8b | OR-S2 | 0.3% | 0.8% |
| qwen3-8b | OR-S3 | 0.1% | 0.4% |
| qwen3-8b | RM-S1 | 1.1% | 1.4% |
| qwen3-8b | RM-S2 | 1.3% | 1.3% |
| qwen3-8b | RM-S3 | 1.0% | 1.1% |

Hallucination on the 15 unanswerable controls (share of answers giving a specific answer):

| model | setup | mono | cross |
|---|---|---|---|
| llama3.1-8b | FC | 8.9% | 5.0% |
| llama3.1-8b | OR-S1 | 7.8% | 5.6% |
| llama3.1-8b | OR-S2 | 1.1% | 3.3% |
| llama3.1-8b | OR-S3 | 12.2% | 5.0% |
| llama3.1-8b | RM-S1 | 4.4% | 4.4% |
| llama3.1-8b | RM-S2 | 1.1% | 2.2% |
| llama3.1-8b | RM-S3 | 6.7% | 5.6% |
| qwen3-8b | FC | 2.2% | 11.7% |
| qwen3-8b | OR-S1 | 7.8% | 15.0% |
| qwen3-8b | OR-S2 | 13.3% | 17.2% |
| qwen3-8b | OR-S3 | 10.0% | 13.3% |
| qwen3-8b | RM-S1 | 6.7% | 12.8% |
| qwen3-8b | RM-S2 | 12.2% | 11.1% |
| qwen3-8b | RM-S3 | 5.6% | 12.8% |

Response language by query and storage language (share of answers):

| model | query | store | en | hg | hi | other |
|---|---|---|---|---|---|---|
| llama3.1-8b | en | en | 99.9% | 0.0% | 0.0% | 0.1% |
| llama3.1-8b | en | hg | 40.0% | 60.0% | 0.0% | 0.0% |
| llama3.1-8b | en | hi | 30.1% | 0.0% | 69.4% | 0.5% |
| llama3.1-8b | hg | en | 14.6% | 85.4% | 0.0% | 0.0% |
| llama3.1-8b | hg | hg | 9.2% | 90.8% | 0.0% | 0.0% |
| llama3.1-8b | hg | hi | 3.9% | 26.9% | 69.2% | 0.0% |
| llama3.1-8b | hi | en | 0.1% | 0.0% | 99.9% | 0.0% |
| llama3.1-8b | hi | hg | 0.8% | 1.9% | 97.4% | 0.0% |
| llama3.1-8b | hi | hi | 0.6% | 0.0% | 99.4% | 0.0% |
| qwen3-8b | en | en | 99.9% | 0.0% | 0.0% | 0.1% |
| qwen3-8b | en | hg | 99.6% | 0.4% | 0.0% | 0.0% |
| qwen3-8b | en | hi | 89.2% | 0.0% | 10.7% | 0.1% |
| qwen3-8b | hg | en | 20.8% | 69.6% | 9.6% | 0.0% |
| qwen3-8b | hg | hg | 17.5% | 78.1% | 3.8% | 0.5% |
| qwen3-8b | hg | hi | 6.7% | 21.1% | 71.9% | 0.3% |
| qwen3-8b | hi | en | 0.6% | 0.0% | 99.4% | 0.0% |
| qwen3-8b | hi | hg | 1.0% | 0.5% | 98.4% | 0.1% |
| qwen3-8b | hi | hi | 1.1% | 0.0% | 98.9% | 0.0% |

## Judge check (judge vs deterministic slot match; human validation not done)

| model | n | judge_correct | slot_match | agreement | kappa | judge_yes_slot_no | judge_no_slot_yes |
|---|---|---|---|---|---|---|---|
| llama3.1-8b | 18900 | 94.7% | 91.9% | 96.2% | 0.697 | 620 | 99 |
| qwen3-8b | 18900 | 92.7% | 90.0% | 95.3% | 0.706 | 693 | 186 |

## Ablations (paired with the main run on the same items)

**A. History length:** Short (10 sessions) vs main (20 sessions), 60 items, q1 only. diff = short − long. Holm over all rows of the table.

| model | setup | cells | items | short_10 | long_20 | diff | CI | p |
|---|---|---|---|---|---|---|---|---|
| llama3.1-8b | FC | mono | 60 | 89.4% | 82.8% | +6.7pp | [+1.1, +12.2] | 0.491 |
| llama3.1-8b | FC | cross | 60 | 82.2% | 80.3% | +1.9pp | [-3.1, +7.2] | 1.000 |
| llama3.1-8b | FC | all | 60 | 84.6% | 81.1% | +3.5pp | [-0.7, +8.0] | 1.000 |
| llama3.1-8b | RM-S1 | mono | 60 | 97.2% | 98.3% | -1.1pp | [-3.3, +1.1] | 1.000 |
| llama3.1-8b | RM-S1 | cross | 60 | 95.8% | 95.6% | +0.3pp | [-1.4, +2.2] | 1.000 |
| llama3.1-8b | RM-S1 | all | 60 | 96.3% | 96.5% | -0.2pp | [-1.7, +1.3] | 1.000 |
| llama3.1-8b | RM-S3 | mono | 60 | 98.9% | 98.9% | +0.0pp | [-1.7, +1.7] | 1.000 |
| llama3.1-8b | RM-S3 | cross | 60 | 96.7% | 96.9% | -0.3pp | [-1.7, +1.1] | 1.000 |
| llama3.1-8b | RM-S3 | all | 60 | 97.4% | 97.6% | -0.2pp | [-1.5, +0.9] | 1.000 |
| qwen3-8b | FC | mono | 60 | 88.9% | 85.6% | +3.3pp | [-0.6, +7.8] | 1.000 |
| qwen3-8b | FC | cross | 60 | 85.3% | 83.3% | +1.9pp | [-1.9, +5.8] | 1.000 |
| qwen3-8b | FC | all | 60 | 86.5% | 84.1% | +2.4pp | [-0.9, +5.7] | 1.000 |
| qwen3-8b | RM-S1 | mono | 60 | 96.1% | 95.0% | +1.1pp | [-1.1, +3.3] | 1.000 |
| qwen3-8b | RM-S1 | cross | 60 | 92.5% | 91.9% | +0.6pp | [-0.8, +1.9] | 1.000 |
| qwen3-8b | RM-S1 | all | 60 | 93.7% | 93.0% | +0.7pp | [-0.6, +2.0] | 1.000 |
| qwen3-8b | RM-S3 | mono | 60 | 96.7% | 94.4% | +2.2pp | [+0.6, +4.4] | 1.000 |
| qwen3-8b | RM-S3 | cross | 60 | 93.1% | 92.8% | +0.3pp | [-0.6, +1.4] | 1.000 |
| qwen3-8b | RM-S3 | all | 60 | 94.3% | 93.3% | +0.9pp | [-0.0, +2.0] | 1.000 |

**B. Indirect questions:** q3 vs q1 (main), 51 items. diff = q3 − q1. Holm over all rows.

| model | setup | cells | items | indirect_q3 | direct_q1 | diff | CI | p |
|---|---|---|---|---|---|---|---|---|
| llama3.1-8b | FC | mono | 51 | 49.7% | 90.8% | -41.2pp | [-49.7, -32.0] | 0.002 |
| llama3.1-8b | FC | cross | 51 | 33.7% | 82.4% | -48.7pp | [-56.5, -41.2] | 0.002 |
| llama3.1-8b | FC | all | 51 | 39.0% | 85.2% | -46.2pp | [-53.4, -39.2] | 0.002 |
| llama3.1-8b | RM-S1 | mono | 51 | 88.2% | 98.7% | -10.5pp | [-17.0, -4.6] | 0.005 |
| llama3.1-8b | RM-S1 | cross | 51 | 85.6% | 95.1% | -9.5pp | [-14.7, -4.6] | 0.005 |
| llama3.1-8b | RM-S1 | all | 51 | 86.5% | 96.3% | -9.8pp | [-15.0, -5.0] | 0.004 |
| llama3.1-8b | RM-S2 | mono | 51 | 86.3% | 98.0% | -11.8pp | [-19.6, -5.2] | 0.005 |
| llama3.1-8b | RM-S2 | cross | 51 | 84.6% | 96.7% | -12.1pp | [-19.0, -5.6] | 0.004 |
| llama3.1-8b | RM-S2 | all | 51 | 85.2% | 97.2% | -12.0pp | [-19.0, -5.9] | 0.004 |
| llama3.1-8b | RM-S3 | mono | 51 | 86.3% | 99.3% | -13.1pp | [-19.6, -7.2] | 0.002 |
| llama3.1-8b | RM-S3 | cross | 51 | 84.3% | 96.1% | -11.8pp | [-18.0, -6.2] | 0.002 |
| llama3.1-8b | RM-S3 | all | 51 | 85.0% | 97.2% | -12.2pp | [-17.6, -7.4] | 0.002 |
| qwen3-8b | FC | mono | 51 | 45.1% | 92.2% | -47.1pp | [-57.5, -35.9] | 0.002 |
| qwen3-8b | FC | cross | 51 | 42.8% | 85.9% | -43.1pp | [-52.6, -33.0] | 0.002 |
| qwen3-8b | FC | all | 51 | 43.6% | 88.0% | -44.4pp | [-53.6, -35.3] | 0.002 |
| qwen3-8b | RM-S1 | mono | 51 | 84.3% | 96.1% | -11.8pp | [-17.6, -5.9] | 0.004 |
| qwen3-8b | RM-S1 | cross | 51 | 76.5% | 90.8% | -14.4pp | [-22.2, -6.5] | 0.004 |
| qwen3-8b | RM-S1 | all | 51 | 79.1% | 92.6% | -13.5pp | [-20.3, -6.8] | 0.003 |
| qwen3-8b | RM-S2 | mono | 51 | 77.1% | 94.8% | -17.6pp | [-25.5, -10.5] | 0.002 |
| qwen3-8b | RM-S2 | cross | 51 | 78.1% | 92.5% | -14.4pp | [-20.3, -8.8] | 0.002 |
| qwen3-8b | RM-S2 | all | 51 | 77.8% | 93.2% | -15.5pp | [-21.6, -9.8] | 0.002 |
| qwen3-8b | RM-S3 | mono | 51 | 86.3% | 96.7% | -10.5pp | [-16.3, -4.6] | 0.005 |
| qwen3-8b | RM-S3 | cross | 51 | 77.1% | 93.5% | -16.3pp | [-23.5, -9.1] | 0.002 |
| qwen3-8b | RM-S3 | all | 51 | 80.2% | 94.6% | -14.4pp | [-20.9, -8.1] | 0.002 |

**C. Devanagari digits:** Hindi storage written with १४-style digits vs Latin digits (main), 50 events, q1. Cells are HI→EN/HI/HG only; 'mono' = HI→HI. diff = Devanagari − Latin. Holm over all rows.

| model | setup | cells | items | devanagari_digits | latin_digits | diff | CI | p |
|---|---|---|---|---|---|---|---|---|
| llama3.1-8b | FC | mono | 50 | 94.0% | 94.0% | +0.0pp | [-6.0, +6.0] | 1.000 |
| llama3.1-8b | FC | cross | 50 | 77.0% | 82.0% | -5.0pp | [-11.0, +1.0] | 1.000 |
| llama3.1-8b | FC | all | 50 | 82.7% | 86.0% | -3.3pp | [-8.0, +1.3] | 1.000 |
| llama3.1-8b | RM-S1 | mono | 50 | 100.0% | 100.0% | +0.0pp | [+0.0, +0.0] | 1.000 |
| llama3.1-8b | RM-S1 | cross | 50 | 97.0% | 97.0% | +0.0pp | [+0.0, +0.0] | 1.000 |
| llama3.1-8b | RM-S1 | all | 50 | 98.0% | 98.0% | +0.0pp | [+0.0, +0.0] | 1.000 |
| llama3.1-8b | RM-S2 | mono | 50 | 96.0% | 96.0% | +0.0pp | [+0.0, +0.0] | 1.000 |
| llama3.1-8b | RM-S2 | cross | 50 | 94.0% | 98.0% | -4.0pp | [-8.0, -1.0] | 1.000 |
| llama3.1-8b | RM-S2 | all | 50 | 94.7% | 97.3% | -2.7pp | [-5.3, -0.7] | 1.000 |
| llama3.1-8b | RM-S3 | mono | 50 | 100.0% | 100.0% | +0.0pp | [+0.0, +0.0] | 1.000 |
| llama3.1-8b | RM-S3 | cross | 50 | 96.0% | 95.0% | +1.0pp | [+0.0, +3.0] | 1.000 |
| llama3.1-8b | RM-S3 | all | 50 | 97.3% | 96.7% | +0.7pp | [+0.0, +2.0] | 1.000 |
| qwen3-8b | FC | mono | 50 | 96.0% | 98.0% | -2.0pp | [-6.0, +0.0] | 1.000 |
| qwen3-8b | FC | cross | 50 | 96.0% | 95.0% | +1.0pp | [+0.0, +3.0] | 1.000 |
| qwen3-8b | FC | all | 50 | 96.0% | 96.0% | +0.0pp | [+0.0, +0.0] | 1.000 |
| qwen3-8b | RM-S1 | mono | 50 | 100.0% | 98.0% | +2.0pp | [+0.0, +6.0] | 1.000 |
| qwen3-8b | RM-S1 | cross | 50 | 98.0% | 98.0% | +0.0pp | [+0.0, +0.0] | 1.000 |
| qwen3-8b | RM-S1 | all | 50 | 98.7% | 98.0% | +0.7pp | [+0.0, +2.0] | 1.000 |
| qwen3-8b | RM-S2 | mono | 50 | 100.0% | 100.0% | +0.0pp | [+0.0, +0.0] | 1.000 |
| qwen3-8b | RM-S2 | cross | 50 | 98.0% | 98.0% | +0.0pp | [+0.0, +0.0] | 1.000 |
| qwen3-8b | RM-S2 | all | 50 | 98.7% | 98.7% | +0.0pp | [+0.0, +0.0] | 1.000 |
| qwen3-8b | RM-S3 | mono | 50 | 100.0% | 100.0% | +0.0pp | [+0.0, +0.0] | 1.000 |
| qwen3-8b | RM-S3 | cross | 50 | 97.0% | 98.0% | -1.0pp | [-3.0, +0.0] | 1.000 |
| qwen3-8b | RM-S3 | all | 50 | 98.0% | 98.7% | -0.7pp | [-2.0, +0.0] | 1.000 |

