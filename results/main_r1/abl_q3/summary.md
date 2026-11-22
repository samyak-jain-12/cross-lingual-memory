# Results summary (abl_q3)

Generations scored: 3672 | answerable: 3672 | models: llama3.1-8b, qwen3-8b

## Accuracy (rows = storage language, columns = query language)

**llama3.1-8b / FC**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 47% | 24% | 33% |
| HI | 47% | 43% | 14% |
| HG | 43% | 41% | 59% |

**llama3.1-8b / RM-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 90% | 90% | 80% |
| HI | 92% | 86% | 73% |
| HG | 90% | 88% | 88% |

**llama3.1-8b / RM-S2**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 90% | 90% | 82% |
| HI | 82% | 82% | 82% |
| HG | 88% | 82% | 86% |

**llama3.1-8b / RM-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 90% | 90% | 80% |
| HI | 92% | 84% | 71% |
| HG | 88% | 84% | 84% |

**qwen3-8b / FC**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 67% | 33% | 39% |
| HI | 67% | 25% | 29% |
| HG | 59% | 29% | 43% |

**qwen3-8b / RM-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 92% | 69% | 69% |
| HI | 86% | 80% | 75% |
| HG | 86% | 75% | 80% |

**qwen3-8b / RM-S2**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 92% | 71% | 71% |
| HI | 90% | 67% | 75% |
| HG | 94% | 69% | 73% |

**qwen3-8b / RM-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 92% | 69% | 69% |
| HI | 90% | 82% | 67% |
| HG | 94% | 75% | 84% |

## H1: monolingual minus cross-lingual accuracy (item-paired, 95% bootstrap CI)

| model | setup | mono | cross | gap | 95% CI |
|---|---|---|---|---|---|
| llama3.1-8b | FC | 50% | 34% | +16.0pp | [+8.5, +23.9] |
| llama3.1-8b | RM-S1 | 88% | 86% | +2.6pp | [-2.3, +7.5] |
| llama3.1-8b | RM-S2 | 86% | 85% | +1.6pp | [-2.6, +5.9] |
| llama3.1-8b | RM-S3 | 86% | 84% | +2.0pp | [-3.9, +7.8] |
| qwen3-8b | FC | 45% | 43% | +2.3pp | [-5.2, +10.1] |
| qwen3-8b | RM-S1 | 84% | 76% | +7.8pp | [+2.6, +14.1] |
| qwen3-8b | RM-S2 | 77% | 78% | -1.0pp | [-5.9, +3.6] |
| qwen3-8b | RM-S3 | 86% | 77% | +9.2pp | [+4.6, +13.7] |

## H2: mirrored directions (item-level exact test; Holm over all 24 tests)

| model | setup | A vs B | items A better / B better | diff (pp) [95% CI] | p | p (Holm) |
|---|---|---|---|---|---|---|
| qwen3-8b | FC | hi->en vs en->hi | 21 / 4 | 33.3 [15.7, 49.0] | 0.0009 | 0.0216 |
| llama3.1-8b | FC | hg->hi vs hi->hg | 16 / 2 | 27.5 [13.7, 41.2] | 0.0013 | 0.0299 |
| qwen3-8b | RM-S2 | hg->en vs en->hg | 14 / 2 | 23.5 [9.8, 37.3] | 0.0042 | 0.0924 |
| qwen3-8b | RM-S3 | hg->en vs en->hg | 16 / 3 | 25.5 [9.8, 41.2] | 0.0044 | 0.0924 |
| qwen3-8b | RM-S3 | hi->en vs en->hi | 13 / 2 | 21.6 [7.8, 35.3] | 0.0074 | 0.148 |
| qwen3-8b | RM-S2 | hi->en vs en->hi | 12 / 2 | 19.6 [7.8, 33.3] | 0.0129 | 0.2451 |
(6 smallest p-values shown; full table in table_mirror.csv)

## Recall@5 (bge-m3), mono vs cross

| strategy | mono R@5 | cross R@5 |
|---|---|---|
| S1 | 99% | 97% |
| S2 | 99% | 100% |
| S3 | 99% | 99% |

Judge vs slot-match agreement (answerable): 94.7% over 3672 responses (disagreements are what the human validation must resolve).
