# Results summary (main_r1)

Generations scored: 41580 | answerable: 37800 | models: llama3.1-8b, qwen3-8b

## Accuracy (rows = storage language, columns = query language)

**llama3.1-8b / FC**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 87% | 69% | 73% |
| HI | 82% | 83% | 67% |
| HG | 88% | 83% | 86% |

**llama3.1-8b / RM-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 98% | 96% | 95% |
| HI | 99% | 96% | 91% |
| HG | 95% | 96% | 97% |

**llama3.1-8b / RM-S2**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 98% | 97% | 96% |
| HI | 96% | 95% | 96% |
| HG | 97% | 96% | 95% |

**llama3.1-8b / RM-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 98% | 96% | 95% |
| HI | 97% | 98% | 94% |
| HG | 97% | 97% | 98% |

**llama3.1-8b / OR-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 100% | 98% | 98% |
| HI | 99% | 97% | 95% |
| HG | 98% | 97% | 98% |

**llama3.1-8b / OR-S2**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 100% | 98% | 98% |
| HI | 97% | 98% | 97% |
| HG | 97% | 98% | 97% |

**llama3.1-8b / OR-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 100% | 98% | 98% |
| HI | 98% | 97% | 96% |
| HG | 98% | 99% | 99% |

**qwen3-8b / FC**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 91% | 78% | 65% |
| HI | 84% | 83% | 80% |
| HG | 91% | 82% | 79% |

**qwen3-8b / RM-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 96% | 91% | 91% |
| HI | 93% | 95% | 93% |
| HG | 96% | 92% | 94% |

**qwen3-8b / RM-S2**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 96% | 93% | 93% |
| HI | 94% | 92% | 91% |
| HG | 96% | 94% | 94% |

**qwen3-8b / RM-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 96% | 91% | 91% |
| HI | 95% | 96% | 94% |
| HG | 97% | 95% | 94% |

**qwen3-8b / OR-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 98% | 93% | 92% |
| HI | 97% | 96% | 96% |
| HG | 97% | 95% | 97% |

**qwen3-8b / OR-S2**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 98% | 93% | 92% |
| HI | 95% | 90% | 91% |
| HG | 97% | 95% | 94% |

**qwen3-8b / OR-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | 98% | 93% | 92% |
| HI | 96% | 97% | 94% |
| HG | 98% | 97% | 98% |

## H1: monolingual minus cross-lingual accuracy (item-paired, 95% bootstrap CI)

| model | setup | mono | cross | gap | 95% CI |
|---|---|---|---|---|---|
| llama3.1-8b | FC | 85% | 77% | +7.9pp | [+5.3, +10.6] |
| llama3.1-8b | RM-S1 | 97% | 95% | +1.8pp | [+0.8, +2.9] |
| llama3.1-8b | RM-S2 | 96% | 96% | -0.2pp | [-1.4, +1.1] |
| llama3.1-8b | RM-S3 | 98% | 96% | +1.8pp | [+0.8, +2.9] |
| llama3.1-8b | OR-S1 | 98% | 98% | +0.7pp | [-0.2, +1.7] |
| llama3.1-8b | OR-S2 | 98% | 98% | +0.7pp | [-0.2, +1.6] |
| llama3.1-8b | OR-S3 | 99% | 98% | +0.8pp | [-0.2, +1.8] |
| qwen3-8b | FC | 84% | 80% | +4.2pp | [+1.8, +6.5] |
| qwen3-8b | RM-S1 | 95% | 93% | +2.6pp | [+1.2, +3.9] |
| qwen3-8b | RM-S2 | 94% | 94% | +0.6pp | [-0.6, +1.9] |
| qwen3-8b | RM-S3 | 95% | 94% | +1.4pp | [+0.1, +2.7] |
| qwen3-8b | OR-S1 | 97% | 95% | +1.9pp | [+0.6, +3.2] |
| qwen3-8b | OR-S2 | 94% | 94% | +0.3pp | [-0.6, +1.3] |
| qwen3-8b | OR-S3 | 98% | 95% | +2.4pp | [+1.2, +3.6] |

## H2: mirrored directions (item-level exact test; Holm over all 42 tests)

| model | setup | A vs B | items A better / B better | diff (pp) [95% CI] | p | p (Holm) |
|---|---|---|---|---|---|---|
| llama3.1-8b | FC | hi->en vs en->hi | 46 / 13 | 13.3 [7.3, 19.3] | 0.0 | 0.0 |
| llama3.1-8b | FC | hg->en vs en->hg | 45 / 9 | 15.7 [10.0, 21.7] | 0.0 | 0.0 |
| llama3.1-8b | FC | hg->hi vs hi->hg | 48 / 13 | 16.0 [10.0, 22.3] | 0.0 | 0.0 |
| qwen3-8b | FC | hg->en vs en->hg | 69 / 2 | 26.3 [21.0, 32.0] | 0.0 | 0.0 |
| qwen3-8b | RM-S3 | hg->en vs en->hg | 20 / 1 | 6.3 [3.7, 9.3] | 0.0 | 0.0 |
| qwen3-8b | OR-S3 | hg->en vs en->hg | 19 / 2 | 5.7 [3.0, 8.7] | 0.0002 | 0.0074 |
(6 smallest p-values shown; full table in table_mirror.csv)

## Recall@5 (bge-m3), mono vs cross

| strategy | mono R@5 | cross R@5 |
|---|---|---|
| S1 | 99% | 98% |
| S2 | 100% | 100% |
| S3 | 99% | 99% |

Judge vs slot-match agreement (answerable): 95.8% over 37800 responses (disagreements are what the human validation must resolve).
