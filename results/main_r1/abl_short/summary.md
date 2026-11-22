# Results summary (abl_short)

Generations scored: 3240 | answerable: 3240 | models: llama3.1-8b, qwen3-8b

## Accuracy (rows = storage language, columns = query language)

**llama3.1-8b / FC**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 92% | 70% | 80% |
| HI | 87% | 87% | 80% |
| HG | 88% | 88% | 90% |

**llama3.1-8b / RM-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 98% | 98% | 97% |
| HI | 95% | 97% | 92% |
| HG | 100% | 93% | 97% |

**llama3.1-8b / RM-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 98% | 98% | 97% |
| HI | 98% | 98% | 95% |
| HG | 95% | 97% | 100% |

**qwen3-8b / FC**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 93% | 83% | 73% |
| HI | 88% | 90% | 83% |
| HG | 95% | 88% | 83% |

**qwen3-8b / RM-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 98% | 85% | 93% |
| HI | 93% | 95% | 93% |
| HG | 95% | 95% | 95% |

**qwen3-8b / RM-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 98% | 85% | 93% |
| HI | 95% | 95% | 95% |
| HG | 95% | 95% | 97% |

## H1: monolingual minus cross-lingual accuracy (item-paired, 95% bootstrap CI)

| model | setup | mono | cross | gap | 95% CI |
|---|---|---|---|---|---|
| llama3.1-8b | FC | 89% | 82% | +7.2pp | [+2.8, +11.4] |
| llama3.1-8b | RM-S1 | 97% | 96% | +1.4pp | [-1.1, +4.2] |
| llama3.1-8b | RM-S3 | 99% | 97% | +2.2pp | [-0.3, +5.3] |
| qwen3-8b | FC | 89% | 85% | +3.6pp | [-1.4, +8.1] |
| qwen3-8b | RM-S1 | 96% | 92% | +3.6pp | [+0.8, +6.9] |
| qwen3-8b | RM-S3 | 97% | 93% | +3.6pp | [+0.8, +6.9] |

## H2: mirrored directions (item-level exact test; Holm over all 18 tests)

| model | setup | A vs B | items A better / B better | diff (pp) [95% CI] | p | p (Holm) |
|---|---|---|---|---|---|---|
| qwen3-8b | FC | hg->en vs en->hg | 14 / 1 | 21.7 [10.0, 33.3] | 0.001 | 0.018 |
| llama3.1-8b | FC | hi->en vs en->hi | 13 / 3 | 16.7 [5.0, 30.0] | 0.0213 | 0.3621 |
| qwen3-8b | RM-S3 | hi->en vs en->hi | 7 / 1 | 10.0 [1.7, 20.0] | 0.0703 | 1.0 |
| llama3.1-8b | FC | hg->en vs en->hg | 7 / 2 | 8.3 [-1.7, 18.3] | 0.1797 | 1.0 |
| qwen3-8b | RM-S1 | hi->en vs en->hi | 7 / 2 | 8.3 [0.0, 18.3] | 0.1797 | 1.0 |
| llama3.1-8b | FC | hg->hi vs hi->hg | 9 / 4 | 8.3 [-3.3, 20.0] | 0.2668 | 1.0 |
(6 smallest p-values shown; full table in table_mirror.csv)

## Recall@5 (bge-m3), mono vs cross

| strategy | mono R@5 | cross R@5 |
|---|---|---|
| S1 | 100% | 100% |
| S2 | 100% | 100% |
| S3 | 100% | 100% |

Judge vs slot-match agreement (answerable): 96.9% over 3240 responses (disagreements are what the human validation must resolve).
