# Endsem plan (19 → 23 Nov 2026)

Goal: run the full study promised in the midsem paper ("Lessons and next steps") and write the final paper by **23 Nov**.
Design stays `phase2/design_spec.md` v1.0; every change is logged in `phase2/DEVIATIONS.md` (#7 onwards).

## 1. Scope

| Block | Items | Cells | Setups | Questions | Readers | Answers |
|---|---|---|---|---|---|---|
| **Main** (Long, ≈20 sessions, distractors on 50%) | 150 + 15 controls | 9 | FC, RM-S1/2/3, OR-S1/2/3 | q1, q2 | Qwen3-8B, Llama-3.1-8B | ≈41.6k |
| **Ablation A: history length** (Short, 10 sessions) | 60 (20 per type) | 9 | FC, RM-S1, RM-S3 | q1 | 2 | ≈3.2k |
| **Ablation B: indirect questions** (q3) | 51 (17 per type) | 9 | FC, RM-S1/2/3 | q3 | 2 | ≈3.7k |
| **Ablation C: Devanagari digits** (१४ vs 14) | 50 events | HI storage × 3 query langs | FC, RM-S1/2/3 | q1 | 2 | ≈1.2k |
| *Optional D: Hinglish with English sentence structure* | 50 | HG storage × 3 | FC, RM-S1 | q1 | 2 | 600 |

Ablation A reverses the spec's direction (spec: Long as ablation). The pilot hit the ceiling rule §8, so Long became the main length and Short is now the comparison.

## 2. Items: 132 still to draft

| Type | Target | Pilot (batch01) | New | Distractors (new / total) | Gender (new) |
|---|---|---|---|---|---|
| Fact | 50 | 10 | 40 | 22 / 25 | 20 F / 20 M |
| Preference | 50 | 10 | 40 | 22 / 25 | 20 F / 20 M |
| Event | 50 | 10 | 40 | 22 / 25 | 20 F / 20 M |
| Unanswerable | 15 | 3 | 12 | — | — |

- Batches: `batch02`–`batch05` with about 10 items per type each, plus `batch06_controls`. Every batch must pass `build_items.py` with **0 errors** before it is merged.
- q3 (indirect question) is written for the first 17 new items of each type.
- Drafted by Claude in the same format as the pilot. **Human verification: decision pending.** Options: (a) a second model cross-checks every HI/HG text, (b) a 10% team spot-check, (c) both, (d) neither, stated as a limitation.

## 3. Pipeline changes (before the main run)

| # | Change | Files |
|---|---|---|
| 1 | Configurable history length (`CLM_SESSIONS`, default 20); evidence slot early/middle/late scaled to the length | `config.py`, `haystack.py`, `build_items.py` |
| 2 | Context limit 16K → about 28K tokens (Hindi ≈ 21K for Qwen at 20 sessions) | `config.py`, `tokens.py` check |
| 3 | Clear Kaggle caches after each model stage | notebook builder |
| 4 | Answer checker: Hindi gender/plural forms (पीला/पीली/पीले) | `textutil.py` |
| 5 | Ablation blocks: q3 query variant, Devanagari digits, Short length | `config.py`, `generate.py`, `retrieve.py`, `report.py` |
| 6 | Merge all batches into one item file `items_main.jsonl` | small script |
| 7 | Mock run of the whole pipeline on CPU (`CLM_BACKEND=mock`), then build the Kaggle notebook | `make_kaggle_notebook.py` |

## 4. Compute (Kaggle 2×T4, 30 GPU-h per account per week)

Estimate: the pilot ran 4.2k answers per reader in about 25 min, mostly on full-context prompts. The main run has 5× the items and 2× longer histories, so about **3–4 h per reader** plus about 1.5 h for the judge. Split it into notebooks so no session nears Kaggle's 12-hour limit:
1. Translate + retrieve + Qwen3-8B reader
2. Llama-3.1-8B reader
3. Judge + report

Each stage caches its outputs, so a crashed session resumes where it stopped. A second team member's Kaggle account can run notebook 2 in parallel.

## 5. Timeline

| Day | Work | Who |
|---|---|---|
| **Wed 19 Nov** | Plan; select candidates; draft batch02–03; pipeline changes 1–4 | Claude |
| **Thu 20 Nov** | Draft batch04–06; QA; (verification option); ablation code; mock test; notebooks | Claude (+ team if verifying) |
| **Fri 21 Nov** | Kaggle runs 1–3 (≈10 GPU-h total) | Team runs, Claude monitors |
| **Sat 22 Nov** | Analysis: pre-registered tests, error taxonomy on about 150 errors, ablations, figures | Claude |
| **Sun 23 Nov** | Final paper (from the midsem LaTeX), Overleaf compile, submit | Claude + team |

**Fallback if Kaggle time runs short:** run the main grid first, then ablations C → B → A (cheapest first). Drop optional D.

## 6. Status log
- 19 Nov: plan written.
- 19 Nov: step 2 done. `src/select_main.py` → `data/candidates/selection_main.csv`: F011–F050, P011–P050, E011–E050 plus 12 controls (`*-ABS`). Every unused screened candidate is used (no spares except 5 RESERVE facts).
- 19 Nov: batch02 drafted (F011–F020, P011–P020, E011–E020) → `data/items/drafts/batch02.json` (parts in `drafts/parts/`). q3 is an indirect wording with the **same gold answer** (no arithmetic), unlike the schema example's 8:45 case; to log as DEVIATIONS #7.
- 19 Nov: batch02 QA passed (0 errors, 0 warnings) → `data/items/items_batch02.jsonl`. Fix: F015 HI q2 reworded (passive "लिया गया था" tripped the gender check). `build_items.py` now also checks q3 for gold leaks and gender; pilot still passes.
- 19 Nov: batch03 drafted (F021–F030, P021–P030, E021–E030) → `data/items/drafts/batch03.json`. Source edits: F021 dropped the "wore 3 shirts" count; E025 dropped the acceptance date (March 20) so only one date is stated; F026 "necklace" → "silver chain" (male user).
- 19 Nov: batch04 drafted (F031–F040, P031–P040, E031–E040) → `data/items/drafts/batch04.json`. Source edits: E033 dropped the rejection date (17th); E032 dropped the price; F038 kept the TD Garden ticket mention as an in-memory near-miss venue.
- 19 Nov: batch05 drafted (F041–F050, P041–P050, E041–E050) → `data/items/drafts/batch05.json`. Source edits: P049 now names the show (Wicked); E049 keeps only February 10 (dropped "and 11th"); E046 says "a studio" not "a yoga studio" (its control asks when yoga classes started); F045 never mentions a brother (its control asks the brother's city).
- 19 Nov: batch05 QA passed first time (0 errors, 0 warnings). **All 150 answerable items built**: 50 per type, 25F/25M per type, 25 distractors per type (exactly 50%), 17 q3 per type, no duplicate IDs.
- 19 Nov: batch06_controls drafted + QA passed (0 errors; gender, base-item and trap-word checks clean) → `data/items/items_batch06_controls.jsonl`. P022-ABS changed from "dish" to "drink" (ramen shop makes "ramen" inferable). **Dataset complete: 150 answerable + 15 controls = 165 items** across `items_batch01_pilot` + `batch02`–`batch05` + `batch06_controls`. Next: pipeline changes (§3).
- 19 Nov: pipeline change 6 done: `src/merge_items.py` → `data/items/items_main.jsonl` (165 items). Evidence position is now a class (early/middle/late) balanced over the whole set within type and distractor status (17/17/16 per type) instead of per batch; ablation flags added (`abl_short` 20/type, `abl_q3` 17/type, `abl_digits` 50 events). Found: the notebook builder bundles only the EN filler pool, so Kaggle would re-translate HI/HG fillers instead of using the frozen ones — fix in change 7.
- 19 Nov: pipeline change 1 done: `config.N_SESSIONS` = 20 (env `CLM_SESSIONS`), position class → slot (4/10/19 at 20, 2/5/9 at 10), Short history = prefix of Long, `banned_fillers` per item (gold value or control answer in filler). Verified for all 495 histories at both lengths. DEVIATIONS #7–#9 logged.
- 19 Nov: pipeline change 2 done: reader context 32,768, judge/translator 8,192 (`config.MODEL_LEN`). Qwen3 token counts for the main set: 20-session Hindi max **23,107** (mean 21,621), fits with ~9.6k to spare; DEVIATIONS #10. Compute note: with a ~59k-token KV cache on 2×T4 only ~2 Hindi histories fit at once, so requests should be grouped by history to keep prefix caching effective (do in change 7).
- 19 Nov: pipeline change 5 done: ablation **blocks** in `config.BLOCKS` (main / short / q3 / digits), run with `CLM_BLOCK`; block-aware item loader, storage languages, query variants and setups; shared translation cache; translator loaded only when needed; Devanagari-digit Hindi histories; FC prompts grouped by history for prefix caching (part of change 7). Mock run of all four blocks on CPU: main 41,580 / short 3,240 / q3 3,672 / digits 1,200 answers per both readers, all stages and reports OK. DEVIATIONS #11. Remaining: change 3 (disk cleanup), 4 (Hindi word forms in the slot checker), 7 (notebooks incl. frozen HI/HG fillers).
- 19 Nov: pipeline change 4 done: lenient slot matching in `textutil.contains` (exact matcher kept as `contains_exact` for data building). Pilot re-score: missed 237 → 134, 0 new false matches, judge agreement 95.6% → 97.0%. DEVIATIONS #12. Remaining: change 3 (disk cleanup) and 7 (notebooks).
- 19 Nov: pipeline changes 3 + 7 done: `src/make_main_notebooks.py main_r1` → `kaggle/main_r1_{1_prep,2_qwen,3_llama,4_judge}.ipynb`. Each bundles code + `items_main.jsonl` + all three **frozen** filler pools, pins vLLM 0.30.0, clears HF/pip caches after each model, restores earlier parts from Add Input, and stops with a clear message if an input is missing. Verified: all cells compile, embedded files byte-identical to the project, CPU mock simulation of the full 1→2/3→4 hand-off produced all four block reports. Not verified: the real GPU run (vLLM install, timings, Llama tokenizer counts). **All pipeline changes done; next is running on Kaggle.**
- 19 Nov: batch04 QA passed first time (0 errors, 0 warnings, extra checks clean) → `data/items/items_batch04.jsonl`.
- 19 Nov: batch03 QA passed first time (0 errors, 0 warnings, extra script/digit/length checks clean) → `data/items/items_batch03.jsonl`.
- 19 Nov: Kaggle part 1 committed as notebook **`clm-main-r1-1-prep`** (account technosam12; `main-r1-1-prep` was taken), Version 1, GPU T4 x2, Internet on, HF_TOKEN attached; status *Queued* for a GPU at commit time. Idle draft session stopped. Parts 2–4 not yet created; in them, Add Input → Your Work → `clm-main-r1-1-prep`.
- 19 Nov: **Part 1 succeeded** (1,590 s, GPU T4 x2; torch 2.13.0+cu130, vLLM 0.30.0, transformers 5.20.2). Translations 1,570 / +66 / +102 / +86 and retrieval 26,730 / 4,860 / 4,131 / 1,350 rankings (main/short/q3/digits), identical to the CPU mock. HI/HG fillers were not re-translated (frozen). Token check, all fit 32,768: Qwen max 23,103 (HI, main), 23,156 (HI, q3); **Llama max 12,801** (HI, main), i.e. ~0.55x Qwen. Output: `clm/results/main_r1/` + results_main_r1_1_prep.zip (8.7 MB). Fixed a cosmetic print (zip name) in the builder for parts 2–4.
- 20 Nov: Parts 2 and 3 committed (`clm-main-r1-2-qwen`, `clm-main-r1-3-llama`), both with `clm-main-r1-1-prep` as input; the account runs both GPU sessions in parallel. Part 2 **Version 1 failed** after ~5 min: `No user secrets exist ... label HF_TOKEN` — the secret tick had not been saved (box showed ticked, reload showed unticked). Re-ticked, verified after a page reload, committed **Version 2**: HF token loaded, part 1 restored, `qwen3-8b: 20790 requests`. Part 3 Version 1: HF token loaded, `llama3.1-8b: 20790 requests`. Lesson for part 4: after ticking HF_TOKEN, reload the editor and confirm it is still ticked before committing.

- **2026-11-20:** Parts 2 and 3 both finished successfully. Qwen (v2) took 41,602 s (~11.6 h); Llama took 17,098 s (~4.7 h). All four blocks are done for both models: main 20,790, short 1,620, q3 1,836, digits 600 answers. Next: part 4 (judge).

- **2026-11-20:** Part 4 (`clm-main-r1-4-judge`, Version 1) **succeeded in 4,807 s (~1.3 h)**. All 3 inputs were restored and HF_TOKEN loaded (the tick was checked again after a reload). Judged: main 41,580, short 3,240, q3 3,672, digits 1,200 (= 2 models × generations). All 4 reports were written. Headline (main, H1 mono − cross gap): FC is Llama +7.9pp [5.3, 10.6] and Qwen +4.2pp [1.8, 6.5]. Retrieval and oracle gaps are about 0–2.6pp. S2 (pivot) closes the gap (Llama −0.2, Qwen +0.6). UI notes: the editor did not draw cells until a session started (Run → Start session); clicks lag about 3 s; one stray Run All was cancelled in cell 1. Next: download `results_main_r1_4_judge.zip` and analyse it locally.

- **2026-11-20:** Downloaded `results_main_r1_4_judge.zip` (10.2 MB; a copy is at `results/results_main_r1_4_judge.zip`). Unpacked to `results/main_r1/` (60 MB) with the main block plus `abl_short/`, `abl_q3/` and `abl_digits/`. Checked: generations, judgments and scored rows match in every block (41,580 / 3,240 / 3,672 / 1,200), and there are 0 UNPARSED judge labels. Next: analysis (pre-registered tests, error taxonomy, ablation comparisons, figures).

- **2026-11-20:** Analysis step 1 done. `src/analyze_main.py main_r1` → `results/main_r1/analysis/analysis.md` + 18 csv files (H1–H4, diagnostic, breakdowns, controls, response language, judge vs slot, ablations A–C). DEVIATIONS #13 (noise-floor scale, Holm families, Friedman next to Cochran's Q). Checked: the digits ablation really uses Devanagari digits (about half of answers differ from main); the q3 drop is real (indirect wording pulls in distractors and abstentions). Still to do: error taxonomy (about 150 errors), figures (needs a matplotlib venv), optional mixed-effects model, paper.

- **2026-11-21:** Verification decision: **no human verification**. Instead, independent-model verification with **Cohere Aya Expanse 8B**, a different family from the Qwen judge and the Llama reader, with Hindi officially supported. It is reported in the paper as model verification, not human. `src/make_verify.py main_r1` → `data/verify/judge_sample.jsonl` (300 answers, stratified by Qwen-judge label: 126 CORRECT, 63 INCORRECT, 63 NO_ANSWER, plus 24 ANSWERED and 24 NO_ANSWER on controls; spread over model × setup × cell; same judge prompt) and `data/verify/item_audit.jsonl` (165 items × HI/HG = 330 audits against English: meaning, key fact, questions, naturalness; JSON output) → `kaggle/verify_aya.ipynb` (self-contained, no inputs; stops early if the HF account lacks Aya access). Needs: Aya licence accepted on HF with the HF_TOKEN account.

- **21 Nov 2026: verification run downloaded.** `clm-main-r1-5-verify-aya` v2 (v1 sat in the queue and was cancelled) ran in 692 s on 2xT4. Aya access OK, rebuilt inputs sha256-identical to `data/verify/`. Outputs in `results/main_r1/verify/` (aya_judge.jsonl 300, aya_audit.jsonl 330) + zip `results/verify_aya_results_main_r1.zip`. All 300 judge replies parse to a label; all 330 audit replies parse as JSON. Next: verification analysis.

- **21 Nov 2026: verification analysis** (`python3 src/analyze_verify.py main_r1` → `results/main_r1/verify/verify.md` + csv). Judge: population-weighted binary agreement 97.6% (answerable), κ 0.80; accuracy under Aya 93.2% vs Qwen 93.7% (−0.5pp [−3.0, +1.2]) → headline accuracies are not a Qwen-judge artefact. Disagreements are mostly Aya's errors: it never outputs NO_ANSWER on answerable items, calls 23/24 fabricated control answers NO_ANSWER, and accepts some wrong dates/places. So the false-abstention and control-hallucination labels are **not** independently confirmed. Audit: 330/330 all-yes, zero problems → rubber-stamp, no evidential value without a planted-error test. H1 sensitivity unchanged (0 items excluded). DEVIATIONS #14.

- **21 Nov 2026: planted-error test of the Aya audit.** `clm-main-r1-6-verify-probe` v2 (v1 queued, cancelled) ran in 543 s; 48 corrupted Hindi/Hinglish items (`src/make_audit_probe.py`, sha256 match). Aya caught **2/48 (4%)**: 0/12 fact swaps, 0/12 fact drops, 1/12 question swaps, 1/12 memory swaps; 0/24 in Hindi. → The translation audit is dropped as evidence; paper states translation quality was **not independently verified** (limitation). Judge verification stands. Outputs `results/main_r1/verify/aya_probe.jsonl`, `audit_probe_scored.csv`, section 4 of `verify.md`; zip `results/verify_aya_probe_main_r1.zip`. DEVIATIONS #14 updated.

- **21 Nov 2026: verification wording for the paper** drafted in `report/verification_wording.md`. Translation checks claimed = what is on record: automatic QA on all 165 items × hi/hg (0 errors; key fact present, no gold leakage, distractor present, gender agreement), pilot LLM review + team spot-check (1 fix), and the team's informal read-through of main-study translations (no per-item labels, so no error rate). Judge verification by Aya as in verify.md. Aya audit mentioned only in Limitations with the 2/48 planted-error result.

- **21 Nov 2026: error taxonomy done** (`make_error_sample.py` → `error_sample.csv`; hand labels `error_labels.csv`; `analyze_errors.py` → `error_taxonomy.md`). 150 errors, weighted shares: **false abstention 48%**, distractor capture 19%, entity substitution 9%, off-task/degenerate 8%, number/date 4%, unsupported 4%, transliteration corruption 3%, partial 1%, inversion <1%; 5% are actually correct (judge false negatives). Abstention is the dominant cross-lingual error (53% cross vs 33% mono) and dominates FC (66%) and Llama (65%). Single AI annotator, disclosed (DEVIATIONS #15). Next: figures.

- **21 Nov 2026: figures done** (`src/make_figures.py`, run with a scratchpad venv that has matplotlib; outputs `report/figures/fig1–4.{pdf,png}`): fig1 3×3 accuracy heatmaps (FC, RM-S1 × both readers), fig2 H1 gap per setup with 95% CI, fig3 cross-lingual recall@5 by strategy × retriever, fig4 error-type shares (mono/cross, FC/RM/OR). Next: write the final paper.
