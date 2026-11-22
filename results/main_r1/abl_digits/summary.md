# Results summary (abl_digits)

Generations scored: 1200 | answerable: 1200 | models: llama3.1-8b, qwen3-8b

## Accuracy (rows = storage language, columns = query language)

**llama3.1-8b / FC**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | nan% | nan% | nan% |
| HI | 86% | 94% | 68% |
| HG | nan% | nan% | nan% |

**llama3.1-8b / RM-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | nan% | nan% | nan% |
| HI | 100% | 100% | 94% |
| HG | nan% | nan% | nan% |

**llama3.1-8b / RM-S2**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | nan% | nan% | nan% |
| HI | 94% | 96% | 94% |
| HG | nan% | nan% | nan% |

**llama3.1-8b / RM-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | nan% | nan% | nan% |
| HI | 98% | 100% | 94% |
| HG | nan% | nan% | nan% |

**qwen3-8b / FC**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | nan% | nan% | nan% |
| HI | 96% | 96% | 96% |
| HG | nan% | nan% | nan% |

**qwen3-8b / RM-S1**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | nan% | nan% | nan% |
| HI | 98% | 100% | 98% |
| HG | nan% | nan% | nan% |

**qwen3-8b / RM-S2**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | nan% | nan% | nan% |
| HI | 98% | 100% | 98% |
| HG | nan% | nan% | nan% |

**qwen3-8b / RM-S3**

| store \ query | EN | HI | HG |
|---|---|---|---|
| EN | nan% | nan% | nan% |
| HI | 96% | 100% | 98% |
| HG | nan% | nan% | nan% |

## H1: monolingual minus cross-lingual accuracy (item-paired, 95% bootstrap CI)

| model | setup | mono | cross | gap | 95% CI |
|---|---|---|---|---|---|
| llama3.1-8b | FC | 94% | 77% | +17.0pp | [+8.0, +26.0] |
| llama3.1-8b | RM-S1 | 100% | 97% | +3.0pp | [+0.0, +7.0] |
| llama3.1-8b | RM-S2 | 96% | 94% | +2.0pp | [-5.0, +9.0] |
| llama3.1-8b | RM-S3 | 100% | 96% | +4.0pp | [+1.0, +8.0] |
| qwen3-8b | FC | 96% | 96% | +0.0pp | [-5.0, +4.0] |
| qwen3-8b | RM-S1 | 100% | 98% | +2.0pp | [+0.0, +6.0] |
| qwen3-8b | RM-S2 | 100% | 98% | +2.0pp | [+0.0, +5.0] |
| qwen3-8b | RM-S3 | 100% | 97% | +3.0pp | [+0.0, +8.0] |

## H2: mirrored directions (item-level exact test; Holm over all 24 tests)

| model | setup | A vs B | items A better / B better | diff (pp) [95% CI] | p | p (Holm) |
|---|---|---|---|---|---|---|
| llama3.1-8b | FC | hi->en vs en->hi | 0 / 0 |  [nan, nan] | 1.0 | 1.0 |
| llama3.1-8b | FC | hg->en vs en->hg | 0 / 0 |  [nan, nan] | 1.0 | 1.0 |
| llama3.1-8b | FC | hg->hi vs hi->hg | 0 / 0 |  [nan, nan] | 1.0 | 1.0 |
| llama3.1-8b | RM-S1 | hi->en vs en->hi | 0 / 0 |  [nan, nan] | 1.0 | 1.0 |
| llama3.1-8b | RM-S1 | hg->en vs en->hg | 0 / 0 |  [nan, nan] | 1.0 | 1.0 |
| llama3.1-8b | RM-S1 | hg->hi vs hi->hg | 0 / 0 |  [nan, nan] | 1.0 | 1.0 |
(6 smallest p-values shown; full table in table_mirror.csv)

## Recall@5 (bge-m3), mono vs cross

| strategy | mono R@5 | cross R@5 |
|---|---|---|
| S1 | nan% | nan% |
| S2 | nan% | nan% |
| S3 | nan% | nan% |

Judge vs slot-match agreement (answerable): 99.2% over 1200 responses (disagreements are what the human validation must resolve).
