# Pilot analysis: `batch01_pilot_r2` (4 Oct 2026)

**Status: PRELIMINARY.** 30 items (+3 unanswerable controls), **draft** HI/HG text (not yet 2-annotator verified), LLM judge **not yet validated** against human labels. Numbers are for pipeline validation and early signals only. Do not present them as findings.

**Run:** Kaggle 2×T4, vLLM 0.30.0, fp16. Readers: Qwen3-8B, Llama-3.1-8B-Instruct. Judge: Qwen3-14B-AWQ. 4,158 answers per reader (33 items × 9 cells × 7 setups × 2 query wordings), 8,316 judgements. Session ≈ 1 h 40 min.

## 1. Data and pipeline quality ✅
- Hinglish fillers: 0/160 turns left in Devanagari (2 needed the romanizing fallback). The first run's 77/160 failure is fixed.
- All 8,316 judge labels parsed; no empty answers; no leaked thinking text; answers ~10 words as instructed.
- **Token cost of storing memory in Hindi** (mean full-context prompt): Qwen3 EN 2,575 / HG 3,615 / **HI 10,456** tokens; Llama-3.1 EN 2,579 / HG 3,605 / **HI 5,834**. The same Hindi history is ~1.8× longer for Qwen than for Llama.

## 2. Main pattern: ceiling effect outside full context
| Setup | Accuracy range across the 9 cells (both models) |
|---|---|
| Full context (FC) | **68–90%** |
| Retrieval (RM-S1/S2/S3) | 83–100% |
| Oracle (OR-S1/S2/S3) | 87–100% |

BGE-M3 finds the memory almost always (R@5 = 98–100% in every cell), so retrieval-memory accuracy is close to oracle. **Pre-registered rule §8 triggers for the retrieval setups** (monolingual EN ≥ 95%, cross cells ≥ 92%): the main run should use a **longer history** and **distractors on 50% of items**. Per DEVIATIONS #5, "long" must be ≈ 20 sessions, not 30 (the Hindi token cost).

## 3. Early signals (n = 30, treat as hypotheses for the main run)
1. **H1 (cross < mono): not detectable yet.** FC gap: Qwen +4.2pp [−0.6, +9.2], Llama +3.6pp [−1.1, +8.6]. The **noise floor is high**: in FC the two wordings of a question disagree on 18–24% of items, so a 4-point gap is within noise.
2. **The question's language matters more than the storage language (FC).** Accuracy by query language: EN 85–88%, HI 78–81%, HG 76–80%. By storage language it's flat (79–84%), with Hinglish storage slightly *best*.
3. **H2 direction effect: exploratory signal only, not significant after correction.** Qwen FC, Hinglish-stored → English-asked vs English-stored → Hinglish-asked:
   - Of 60 question pairs (30 items × 2 wordings), 45 had the same outcome in both directions. Of the 15 that differed, 13 favoured HG→EN and 2 favoured EN→HG. Pair-level exact McNemar p = 0.007, but the two wordings of an item are not independent.
   - **Item-level** (the correct unit): HG→EN better on 11 items, EN→HG on 2, exact **p = 0.022**. Accuracy difference **+18.3pp, 95% CI [6.7, 31.7]** (bootstrap; `table_mirror.csv`).
   - The mirror table ran **42 tests** (2 models × 7 setups × 3 pairs); about 2 false positives are expected at α = 0.05. Holm across all 42 → **not significant**.
   - Llama points the same way (10 vs 3 pairs). Treat as a hypothesis for the pre-registered main-run test (150 items).
4. **RQ4: representation matters for retrieval, clearly for lexical search.**
   - BM25 on original text (S1) **collapses across scripts**: EN↔HI R@5 ≈ 47% vs 93% within a language. Translating everything to English (S2) restores it: cross R@5 61% → **93%**.
   - Dense retrievers are robust at top-5, but lose at **top-1** cross-lingually: BGE-M3 R@1 87% → 82%, mE5 89% → 79%. **S2 removes the top-1 gap** (BGE-M3 89/89, mE5 93/92).
5. **Errors are mostly "I don't know", not distortions.** FC errors: Qwen 69/105 and Llama 71/97 are false abstentions; distractor capture is rare (3–10%). The models fail to *find* the memory in a long history more often than they misremember it.
6. **Events are easy, facts and preferences are not.** FC: events 93–98%, facts 73–77%, preferences 71–76%. Explicit dates are salient.
7. **Answer language.** Qwen answers in the question's language 96% of the time. **Llama answers English questions in Hindi or Hinglish 45% of the time**, following the history's language (cf. OLA, XRAG). Both models answer Hinglish questions in Devanagari 24–29% of the time.
8. **Hallucination on unanswerable controls:** Qwen 15–26%, Llama 2–13% depending on setup. Example: Llama invented an app name ("Focus@will") for "Which audiobook app do I use?". Only 3 control items, so very noisy.

## 4. Measurement issues found (fix before the main run)
| Issue | Evidence | Fix |
|---|---|---|
| Slot checker misses Hindi inflections | 301 answers judged CORRECT without a slot match, e.g. "पीला ड्रेस" vs alias "पीली ड्रेस" | Add inflected variants during verification; keep the judge as primary, pending κ |
| Judge sometimes too strict on Hinglish | e.g. "Aapne University of Melbourne mein study abroad…" judged INCORRECT | Human validation (200 rows, `judge_validation_sample.csv`) → κ; revise the judge prompt if κ < 0.80 |
| Disk nearly full on Kaggle (59.4 / 57.6 GiB) | Kaggle warning during the judge stage | Clear the HF xet/pip caches and embedder models after each stage |

## 5. Next steps
1. Team: verify the pilot items (`data/items/verify_batch01_pilot.xlsx`) and label the 200 judge-validation rows.
2. Main-run design per rule §8: ≈ 20-session histories (raise `MAX_MODEL_LEN` to fit Hindi ≈ 21k Qwen tokens), distractors on 50% of items. Log as a deviation.
3. Draft the remaining 120 items.

## 6. Judge check (added 12 Oct)
Qwen3-14B judge vs an independent **LLM annotator (Claude)** on the 200-row stratified sample: **96.5% agreement, κ = 0.85** (3 labels); **98.5%** on correct-vs-not. Of the 3 accuracy-relevant disagreements, 2 are invented answers to unanswerable questions that the judge accepted as "don't know", so the hallucination rates above are slight **under**-estimates; 1 is a mistranslated answer ("short *wheat* rice") the judge accepted. This is **not** human validation; the human columns of `judge_validation_batch01_pilot_r2.xlsx` remain empty.

## 7. Figures
`report/figures/batch01_pilot_r2/`: fig1 full-context 3×3 heatmaps · fig2 Recall@1 by retriever × strategy · fig3 token cost by storage language · fig4 accuracy by question vs storage language. Regenerate with `python src/make_figures.py <run>`.
