# Independent-model verification of `main_r1` (Aya Expanse 8B)

Aya Expanse 8B (Cohere; a different model family from the Qwen judge and both readers) re-labelled a stratified sample of 300 judge decisions with the judge's exact prompt, and audited every item's Hindi and Hinglish text against the English source. This is **independent-model verification, not human verification**.

Aya replies parsed: judge 300/300.

## 1. Judge agreement

Sample stratified by the Qwen label. *Population* figures re-weight each stratum to its share of all 41,580 judgments; 95% CI by stratified bootstrap.

| items | qwen | n | population_share | aya_same | aya_labels |
|---|---|---|---|---|---|
| control | ANSWERED | 24 | 0.8% | 4.2% | NO_ANSWER 23, ANSWERED 1 |
| control | NO_ANSWER | 24 | 8.3% | 100.0% | NO_ANSWER 24 |
| answerable | CORRECT | 126 | 85.2% | 98.4% | CORRECT 124, INCORRECT 2 |
| answerable | INCORRECT | 63 | 4.2% | 79.4% | INCORRECT 50, CORRECT 13 |
| answerable | NO_ANSWER | 63 | 1.5% | 0.0% | INCORRECT 63 |

| set | n | raw_agree_sample | pop_agree | pop_kappa | pop_agree_binary | pop_kappa_binary |
|---|---|---|---|---|---|---|
| answerable | 252 | 69.0% | 95.9% [93.5%, 97.6%] | 0.67 [0.55, 0.79] | 97.6% [95.1%, 99.3%] | 0.80 [0.66, 0.93] |
| controls | 48 | 52.1% | 92.0% [91.7%, 92.7%] | 0.07 [0.00, 0.21] | 92.0% [91.7%, 92.7%] | 0.07 [0.00, 0.21] |
| all | 300 | 66.3% | 95.5% [93.4%, 97.1%] | 0.83 [0.76, 0.89] | 97.0% [94.9%, 98.6%] | 0.75 [0.63, 0.87] |

*binary* = the distinction the accuracy metric uses (answerable: CORRECT vs not; controls: NO_ANSWER vs not).

Confusion on the sample (rows Qwen, columns Aya; raw counts):

| qwen \ aya | CORRECT | INCORRECT | NO_ANSWER | ANSWERED | UNPARSED |
|---|---|---|---|---|---|
| CORRECT | 124 | 2 | 0 | 0 | 0 |
| INCORRECT | 13 | 50 | 0 | 0 | 0 |
| NO_ANSWER | 0 | 63 | 24 | 0 | 0 |
| ANSWERED | 0 | 0 | 23 | 1 | 0 |

**Accuracy implied by each judge** (answerable items, population-weighted): Qwen 93.7%, Aya 93.2%; difference Aya − Qwen -0.5pp [-3.0, +1.2].

**Agreement with slot match** (rule-based; population-weighted): Qwen 96.2%, Aya 94.6%.

Binary agreement on the sample by cell type (unweighted): cross 93.5% (n=170); mono 95.1% (n=82)

## 2. Item audit (Hindi and Hinglish vs English source)

330 audits = 165 items × 2 languages. Share answered **no** per check:

| language | n | meaning_same | key_fact_present | questions_same | natural | any core fail |
|---|---|---|---|---|---|---|
| hi | 165 | 0/165 | 0/150 | 0/165 | 0/165 | 0/165 |
| hg | 165 | 0/165 | 0/150 | 0/165 | 0/165 | 0/165 |

Items failing a core check in at least one language: **0** (none). Full list with Aya's notes: `audit_flagged.csv`.

## 3. Sensitivity: H1 gap without items that fail a core audit check

Gap = mono − cross accuracy, item-paired, 95% bootstrap CI; *clean* drops the 0 items above.

| model | setup | gap_all | n_all | gap_clean | n_clean | change |
|---|---|---|---|---|---|---|
| llama3.1-8b | FC | +7.9pp [+5.4, +10.5] | 150 | +7.9pp [+5.4, +10.6] | 150 | +0.0pp |
| llama3.1-8b | RM-S1 | +1.8pp [+0.8, +2.9] | 150 | +1.8pp [+0.8, +2.9] | 150 | +0.0pp |
| llama3.1-8b | RM-S2 | -0.2pp [-1.4, +1.1] | 150 | -0.2pp [-1.4, +1.1] | 150 | +0.0pp |
| llama3.1-8b | RM-S3 | +1.8pp [+0.7, +2.9] | 150 | +1.8pp [+0.8, +3.0] | 150 | +0.0pp |
| llama3.1-8b | OR-S1 | +0.7pp [-0.2, +1.7] | 150 | +0.7pp [-0.2, +1.7] | 150 | +0.0pp |
| llama3.1-8b | OR-S2 | +0.7pp [-0.2, +1.6] | 150 | +0.7pp [-0.2, +1.6] | 150 | +0.0pp |
| llama3.1-8b | OR-S3 | +0.8pp [-0.2, +1.8] | 150 | +0.8pp [-0.2, +1.7] | 150 | +0.0pp |
| qwen3-8b | FC | +4.2pp [+1.8, +6.5] | 150 | +4.2pp [+1.7, +6.5] | 150 | +0.0pp |
| qwen3-8b | RM-S1 | +2.6pp [+1.2, +3.9] | 150 | +2.6pp [+1.2, +3.9] | 150 | +0.0pp |
| qwen3-8b | RM-S2 | +0.6pp [-0.7, +1.8] | 150 | +0.6pp [-0.7, +1.9] | 150 | +0.0pp |
| qwen3-8b | RM-S3 | +1.4pp [+0.1, +2.7] | 150 | +1.4pp [+0.1, +2.7] | 150 | +0.0pp |
| qwen3-8b | OR-S1 | +1.9pp [+0.6, +3.1] | 150 | +1.9pp [+0.6, +3.2] | 150 | +0.0pp |
| qwen3-8b | OR-S2 | +0.3pp [-0.6, +1.3] | 150 | +0.3pp [-0.6, +1.3] | 150 | +0.0pp |
| qwen3-8b | OR-S3 | +2.4pp [+1.2, +3.6] | 150 | +2.4pp [+1.2, +3.6] | 150 | +0.0pp |

## 4. Planted-error test of the audit (`src/make_audit_probe.py`)

48 deliberately broken translations (key fact swapped or deleted, q1 or memory_turn replaced by another item's) in the exact audit prompt. *Caught* = Aya answers no to a check the corruption breaks.

| group | n | caught_expected_check | caught_any_core_check |
|---|---|---|---|
| fact_drop | 12 | 0/12 | 0/12 |
| fact_swap | 12 | 0/12 | 0/12 |
| memory_swap | 12 | 1/12 | 1/12 |
| question_swap | 12 | 1/12 | 1/12 |
| hg | 24 | 2/24 | 2/24 |
| hi | 24 | 0/24 | 0/24 |
| all | 48 | 2/48 | 2/48 |

**Detection rate 4.2%.** The audit cannot tell broken translations from good ones, so its 330/330 pass is **not evidence of translation quality** and is not reported as such.

