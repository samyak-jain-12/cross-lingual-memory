# Filler pools (frozen 2026-10-12)

- `filler_pool_en.jsonl`: 40 sessions from LongMemEval-S (build_filler_pool.py).
- `filler_pool_hi.jsonl`, `filler_pool_hg.jsonl`: machine translations by Qwen3-8B from run `batch01_pilot_r2` (few-shot Hinglish prompt, DEVIATIONS #4). **Frozen**: every later run uses these exact files (`haystack.filler_path` prefers `data/haystacks/`).
- Quality: 0/160 Hinglish turns in Devanagari; 1/160 left in English (FL03 assistant turn) -> hand-translated to Hinglish by Claude on 2026-10-12.
- 10% spot check (FL03, FL28, FL31, FL37): fluent, with minor mistranslations in Hindi filler (e.g. FL03 Sunday -> शनिवार; FL31 "weekend-long" -> six-day) and some तुम/आप register mixing. Fillers are never scored, so these were left as is (noted as a limitation).
