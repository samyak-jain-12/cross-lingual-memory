# Verification paragraphs for the final paper (draft, 21 Nov 2026)

Every claim below has a record in the repo (source in brackets). The bracketed notes are for us, not the paper.

## Methods: translation checks

The Hindi and Hinglish versions of every item were checked in three ways. First, an automatic check ran on all
165 items in both languages before the items were frozen. It confirmed that the key fact appears in the translated
memory turn, that the gold answer does not leak into any other turn, that each distractor value appears in its
distractor sentence, and that first-person verb forms agree with the user's gender. All batches passed with zero
errors. Second, the 33 pilot items were reviewed by an LLM and spot-checked by the team, which led to one
correction. Third, the team read through the main-study translations and found them largely correct, but did not
record per-item error labels, so we cannot report an error rate.

[Sources: `src/build_items.py` checks, `data/items/qa_batch0*.txt` (0 errors), README pilot row (LLM review +
team spot-check, fix E007). The third sentence is the team's informal read-through, as you describe it; only keep
it if that is what happened, and keep "did not record per-item error labels".]

## Methods: independent-model verification of the judge

We re-labelled a stratified sample of 300 judge decisions with Aya Expanse 8B, a model from a different family
than both the judge and the readers, using the judge's exact prompt. Re-weighted to the full label mix, the two
models agree on whether an answer is correct in 97.6% of cases (95% CI 95.1–99.3; Cohen's κ = 0.80). Accuracy
implied by Aya is 93.2% against 93.7% for the Qwen judge (difference −0.5 pp, CI −3.0 to +1.2), so the headline
accuracies are not an artefact of the judge. Aya does not use the NO_ANSWER label for answerable items, and on
unanswerable controls it labels fabricated answers as abstentions; the abstention and control-hallucination
labels are therefore not independently confirmed.

## Limitations

Translation quality was checked automatically for the key fact, leakage and gender agreement, but there was no
formal human annotation with error labels for the main study. We also asked Aya to audit the translations, but
in a planted-error test it caught only 2 of 48 deliberately broken items, so we do not use that audit as
evidence. A native-speaker annotation of the translations is left for future work.

[Sources: `results/main_r1/verify/verify.md` sections 1, 2, 4; DEVIATIONS #14.]
