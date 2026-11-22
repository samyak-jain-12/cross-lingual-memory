# Results summary (batch01_pilot_r2)

Generations scored: 8316 | answerable: 7560 | models: llama3.1-8b, qwen3-8b

## Accuracy (rows = storage language, columns = query language)

**llama3.1-8b / FC**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 90% | 77% | 77% |
| HI | 85% | 78% | 78% |
| HG | 88% | 80% | 85% |

**llama3.1-8b / RM-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 97% | 97% | 93% |
| HI | 98% | 97% | 90% |
| HG | 98% | 92% | 90% |

**llama3.1-8b / RM-S2**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 97% | 95% | 97% |
| HI | 97% | 97% | 97% |
| HG | 98% | 97% | 97% |

**llama3.1-8b / RM-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 97% | 97% | 93% |
| HI | 100% | 97% | 90% |
| HG | 98% | 95% | 97% |

**llama3.1-8b / OR-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 100% | 98% | 98% |
| HI | 100% | 97% | 98% |
| HG | 100% | 87% | 97% |

**llama3.1-8b / OR-S2**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 100% | 98% | 98% |
| HI | 100% | 100% | 95% |
| HG | 100% | 98% | 93% |

**llama3.1-8b / OR-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 100% | 98% | 98% |
| HI | 100% | 97% | 93% |
| HG | 98% | 95% | 95% |

**qwen3-8b / FC**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 90% | 80% | 68% |
| HI | 78% | 80% | 78% |
| HG | 87% | 83% | 80% |

**qwen3-8b / RM-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 92% | 87% | 90% |
| HI | 92% | 88% | 85% |
| HG | 93% | 90% | 93% |

**qwen3-8b / RM-S2**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 92% | 83% | 83% |
| HI | 90% | 88% | 87% |
| HG | 92% | 95% | 97% |

**qwen3-8b / RM-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 92% | 87% | 90% |
| HI | 93% | 92% | 88% |
| HG | 95% | 95% | 93% |

**qwen3-8b / OR-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 97% | 95% | 95% |
| HI | 98% | 93% | 93% |
| HG | 97% | 95% | 95% |

**qwen3-8b / OR-S2**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 97% | 95% | 95% |
| HI | 97% | 95% | 92% |
| HG | 98% | 97% | 100% |

**qwen3-8b / OR-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 97% | 95% | 95% |
| HI | 100% | 97% | 95% |
| HG | 97% | 100% | 100% |

## H1: monolingual minus cross-lingual accuracy (item-paired, 95% bootstrap CI)

| model | setup | mono | cross | gap | 95% CI |
|---|---|---|---|---|---|
| llama3.1-8b | FC | 84% | 81% | +3.6pp | [-1.1, +8.6] |
| llama3.1-8b | RM-S1 | 94% | 95% | -0.3pp | [-3.9, +3.3] |
| llama3.1-8b | RM-S2 | 97% | 97% | +0.0pp | [-2.2, +2.2] |
| llama3.1-8b | RM-S3 | 97% | 96% | +1.1pp | [-2.5, +4.4] |
| llama3.1-8b | OR-S1 | 98% | 97% | +0.8pp | [-1.7, +3.3] |
| llama3.1-8b | OR-S2 | 98% | 98% | -0.6pp | [-2.2, +0.8] |
| llama3.1-8b | OR-S3 | 97% | 97% | +0.0pp | [-2.8, +2.5] |
| qwen3-8b | FC | 83% | 79% | +4.2pp | [-0.6, +9.2] |
| qwen3-8b | RM-S1 | 91% | 89% | +1.7pp | [-0.8, +4.4] |
| qwen3-8b | RM-S2 | 92% | 88% | +3.9pp | [+0.6, +7.8] |
| qwen3-8b | RM-S3 | 92% | 91% | +0.8pp | [-1.9, +3.6] |
| qwen3-8b | OR-S1 | 95% | 96% | -0.6pp | [-3.6, +2.5] |
| qwen3-8b | OR-S2 | 97% | 96% | +1.7pp | [+0.3, +3.3] |
| qwen3-8b | OR-S3 | 98% | 97% | +0.8pp | [-1.4, +3.1] |

## H2: mirrored directions (item-level exact test; Holm over all 42 tests)

| model | setup | A vs B | items A better / B better | diff (pp) [95% CI] | p | p (Holm) |
|---|---|---|---|---|---|---|
| qwen3-8b | FC | hg->en vs en->hg | 11 / 2 | 18.3 [6.7, 31.7] | 0.0225 | 0.945 |
| llama3.1-8b | OR-S1 | hg->hi vs hi->hg | 0 / 6 | -11.7 [-21.7, -3.3] | 0.0312 | 1.0 |
| llama3.1-8b | FC | hi->en vs en->hi | 5 / 1 | 8.3 [0.0, 18.3] | 0.2188 | 1.0 |
| qwen3-8b | RM-S2 | hg->en vs en->hg | 5 / 1 | 8.3 [0.0, 18.3] | 0.2188 | 1.0 |
| llama3.1-8b | FC | hg->en vs en->hg | 8 / 3 | 11.7 [-1.7, 25.0] | 0.2266 | 1.0 |
| qwen3-8b | RM-S2 | hg->hi vs hi->hg | 3 / 0 | 8.3 [0.0, 18.3] | 0.25 | 1.0 |
(6 smallest p-values shown; full table in table_mirror.csv)

## Recall@5 (bge-m3), mono vs cross

| strategy | mono R@5 | cross R@5 |
|---|---|---|
| S1 | 98% | 99% |
| S2 | 100% | 100% |
| S3 | 99% | 99% |

Judge vs slot-match agreement (answerable): 95.6% over 7560 responses (disagreements are what the human validation must resolve).
