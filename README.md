# Cross-Lingual Memory in LLM Agents

Course research project (Aug–Nov 2026). Does an LLM agent still recall what a user told it when the language used to **store** a memory (English / Hindi / Hinglish) differs from the language used to **ask** about it?

## Where things are
| Folder | Contents | Status |
|---|---|---|
| `phase1/` | Literature review, comparison table, related-work draft, `references.bib` | Done 2 Oct |
| `phase2/` | `design_spec.md` (frozen design v1.0), `item_schema_example.json`, `power_analysis.py`, `DEVIATIONS.md` | Done 2 Oct |
| `data/raw/` | `longmemeval_oracle.json` (MIT, HF `xiaowu0162/longmemeval-cleaned`), `locomo10.json` (CC BY-NC 4.0, backup only). Downloaded 2 Oct 2026. | — |
| `data/candidates/` | `candidates.csv` (177 LongMemEval candidates, screened with reasons), `pref_extra.csv` (33 extra preferences mined from LongMemEval-S) | Done 3 Oct |
| `data/items/` | `drafts/batch01_pilot.json` (30 items + 3 controls, EN/HI/HG), `items_batch01_pilot.jsonl` (built), `qa_batch01_pilot.txt` (0 errors), `verify_batch01_pilot.xlsx` (for the team) | Pilot drafted 3 Oct; LLM review + informal team spot-check 12 Oct (1 fix: E007 bike→cycle) |
| `data/haystacks/` | 40 filler sessions in EN/HI/HG, **frozen** 12 Oct (see its README) | Done |
| `src/` | `build_candidates.py` → `apply_screening.py` → `mine_preferences.py` → `build_items.py` → `make_verification_sheet.py` → `build_filler_pool.py` | Phase 3 scripts |
| `src/clm/` | Experiment pipeline: `translate → retrieve → tokens → generate (×2 readers) → judge → report`. Test on CPU with `CLM_BACKEND=mock` | Built + mock-tested 3 Oct |
| `kaggle/` | `clm_batch01_pilot_r2.ipynb`: self-contained notebook (code + pilot data). Rebuild with `python src/make_kaggle_notebook.py <batch> [run]` | Ran 4 Oct |
| `results/batch01_pilot_r2/` | Pilot results (30 items, 2 readers, judge) + `ANALYSIS.md`, judge-validation workbook | Done 4 Oct; analysed 12 Oct |
| `report/figures/` | Report figures (`src/make_figures.py <run>`) | Done 12 Oct |
| `report/paper/` | Midsem paper (LaTeX, course ACL template, **compile with LuaLaTeX**) + `paper_overleaf.zip` for upload | Draft 12 Oct |

## Timeline
Midsem report 7 Oct · dataset frozen 19 Oct · pilot by 24 Oct · main runs by 7 Nov · analysis by 16 Nov · final report end Nov.
