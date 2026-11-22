# Phase 2 — Experimental Design Specification
**Project:** Cross-Lingual Memory in LLM Agents
**Version:** v1.0 (frozen 2 Oct 2026). Any change after this goes in `phase2/DEVIATIONS.md` with date + reason.
**Depends on:** `phase1/phase1_literature_review.md` (citations), `data/raw/` (source data, inspected 2 Oct 2026)

> Marking convention: **[DECIDED]** = fixed for the study · **[ABLATION]** = run on a subset only · **[OPTIONAL]** = only if ahead of schedule · **[CHECK IN PHASE 4]** = assumption we must verify when code runs.

---

## 0. One-paragraph design summary

We build **150 personal memory items** (50 facts, 50 preferences, 50 events), plus **15 unanswerable controls**, from LongMemEval. Each item exists in three **parallel versions**: English (EN), Hindi in Devanagari (HI) and romanized Hinglish (HG), all verified by humans. For every item, we write the user's conversation history entirely in a **storage language** L_s. We then ask about the memory in a new session, in a **query language** L_q. Crossing L_s × L_q gives a **3×3 grid** (MLQA's G-XLT design applied to agent memory). Each cell runs under three **memory setups**:
- **full context:** the whole history goes in the prompt
- **retrieval memory**, with three storage strategies:
  - **S1 original:** keep the text as written
  - **S2 English pivot:** translate the memories (and the query) to English
  - **S3 dual:** store both the original and the English translation
- **oracle:** the model is handed the gold memory directly

We use **two open 8B readers** (Qwen3-8B and Llama-3.1-8B-Instruct) and score answers with:
- an LLM judge, validated against human labels
- a deterministic slot checker
- an error taxonomy

Comparing **retrieval recall, reading-given-retrieval and oracle accuracy** tells us *where* a cross-lingual memory fails.

---

## 1. Research questions → operational hypotheses → tests

| RQ | Hypothesis (directional) | Measured as | Primary test |
|---|---|---|---|
| **RQ1** Does accuracy drop when L_s ≠ L_q? | **H1:** cross-lingual cells < monolingual cells. The drop is larger for retrieval memory than for full context. | Item-level mean accuracy over the 6 off-diagonal cells vs the 3 diagonal cells | Paired permutation test on item means (10k permutations); bootstrap 95% CI on the gap |
| **RQ2** Are directions asymmetric? | **H2:** X→EN > EN→X (memory stored in Hindi/Hinglish, asked in English, beats the reverse) | Mirrored pairs: (HI→EN vs EN→HI), (HG→EN vs EN→HG), (HG→HI vs HI→HG) | Exact McNemar per pair, Holm-corrected within each reader × setup |
| **RQ3** Does code-switching add errors? | **H3 (two-sided, an open question):** Hinglish queries differ from Devanagari Hindi queries over the same stored memory. Lit. points both ways (Chirkova 2024 vs Mohamed 2025). | Acc(s→HG) vs Acc(s→HI) for s ∈ {EN, HI}; and Acc(HG→HG) vs Acc(HI→HI) | Exact McNemar, Holm |
| **RQ4** Which representation preserves memory best? | **H4:** S3 dual ≥ S2 pivot > S1 original on cross-lingual cells. S2 loses on names and numbers. | Accuracy and recall@5 per strategy, pooled over off-diagonal cells | Cochran's Q across S1/S2/S3, then McNemar S3–S1, S2–S1, S3–S2 (Holm) |
| **Diagnostic** Where does it fail? | Cross-lingual losses come from *both* retrieval and reading (XBCP 2026 precedent) | Retrieval miss = 1 − R@5; reading error = P(wrong \| gold retrieved); oracle error | Descriptive, with bootstrap CIs; stacked bar per cell |

**Unit of analysis:** the item, always paired across conditions.
**α = 0.05**, two-sided, with **Holm** correction inside each family of tests.
We report effect sizes (percentage-point gap with 95% CI) alongside every p-value.

**Secondary model (robustness):** a mixed-effects logistic regression with predictors storage language × query language × strategy, a random intercept per item, and fixed effects for reader and memory type. It's reported for completeness, not used to accept or reject hypotheses.

### 1.1 Power (from `phase2/power_analysis.py`)
Exact McNemar, α = .05, 3,000 simulations. "Discordant" is the share of items answered correctly in exactly one of the two conditions being compared:

| n items | discordant 15% | discordant 25% | discordant 35% |
|---|---|---|---|
| 100 | 10pp gap → 0.70 | 10pp → 0.43 | 10pp → 0.33 |
| **150** | **10pp → 0.90** | **10pp → 0.64 · 12pp → 0.82** | 12pp → 0.66 · 15pp → 0.87 |
| 200 | 10pp → 0.96 | 10pp → 0.78 | 12pp → 0.81 |

**[DECIDED] n = 150 answerable items.** At realistic discordance (~25%) we can reliably detect gaps of **about 12pp or more** in a single pairwise test. Smaller gaps get reported descriptively, not claimed. The pooled H1 test averages 6 cells per item, so it has more power than any single pairwise test. Going to 200 items isn't worth the extra translation and verification work.

### 1.2 Noise floor (Mukherjee et al. 2026 warning)
Greedy decoding is deterministic, so we can't measure noise by re-running the same prompt. Instead:
- **[DECIDED]** every item has **two equivalent query paraphrases (q1, q2)** in every language.
- The **paraphrase disagreement rate** on monolingual cells, P(q1 correct ≠ q2 correct), is our noise floor.
- A cross-lingual gap smaller than this noise floor is labeled "not distinguishable from noise".

---

## 2. Definitions

### 2.1 Languages [DECIDED]
| Code | Definition | Conventions |
|---|---|---|
| **EN** | English | As in source data, lightly edited |
| **HI** | Standard conversational Hindi, **Devanagari script** | Natural spoken register, not Sanskritized. Common English loanwords are fine in Devanagari (ऑफिस, मीटिंग). **Brand / product names stay in Latin** (Sony A7R IV). **Person and place names in Devanagari** (पुणे). **Arabic digits** (15 मार्च, 45 मिनट). |
| **HG** | **Romanized Hindi–English code-mixed text**, Hindi grammatical frame with English insertions, as in urban chat | No diacritics. Fixed spellings (§2.2). English content words and brand names stay English. Arabic digits. |

**Grammatical gender & address [DECIDED]**
- Hindi first-person verbs mark gender (सुनता हूँ vs सुनती हूँ). Each item fixes `user_gender` (balanced **50/50 within each memory type**), and HI and HG must use it consistently.
- The assistant always addresses the user as **आप / aap**.
- EN carries no gender marking. Gender is a balanced nuisance variable, not a hypothesis.

### 2.2 Hinglish spelling sheet [DECIDED, extend in Phase 3]
`hai, hain, hoon, tha, thi, the, nahi, toh, par, aur, yeh, woh, kya, kyun, mera, meri, mere, main (I), mein (in), mujhe, aap, ka, ki, ke, ko, se, ke liye, kal, aaj, abhi, bahut, accha, pasand, chahiye, gaya, gayi, karta/karti, raha/rahi, wala/wali`
Rule: if a word isn't on the sheet, use the most common chat spelling. When unsure, both annotators agree and we add it to the sheet.

### 2.3 Memory types [DECIDED]
| Type | Definition | Answer slot | Example |
|---|---|---|---|
| **Fact** | Stable personal attribute the user stated | entity / quantity / name | "my commute is 45 minutes each way" → *45 minutes* |
| **Preference** | Something the user likes, uses or prefers | the preferred entity | "I enjoy using Adobe Premiere Pro" → *Adobe Premiere Pro* |
| **Event** | Something that happened to the user, with an explicit date | date and/or event entity | "got my car serviced for the first time on March 15th" → *March 15* |

### 2.4 Correctness [DECIDED]
A response is **correct** if it states every gold slot (any accepted alias, any script) and doesn't contradict the gold answer. Answering in the "wrong" language is **not** an error for accuracy; we log it separately (§6). Hedged-but-right ("I think 45 minutes") counts as correct. Listing several candidates with the gold among them is **incorrect**.

---

## 3. Data

### 3.1 Source [DECIDED]: LongMemEval (MIT licence)
Checked on `data/raw/longmemeval_oracle.json` (500 questions):

| LongMemEval type | Count | Single user-evidence turn | Use |
|---|---|---|---|
| single-session-user | 64 (+6 abstention) | 64 | **Fact pool** (take 50) |
| single-session-preference | 30 | 19 | **Preference pool.** LongMemEval answers are rubric-style ("the user would prefer…"), so **each one gets rewritten as a short-answer question** ("Which video editing software do I like to use?" → *Adobe Premiere Pro*). Top up to 50 from preference statements inside other items' user turns. |
| temporal-reasoning / multi-session | 127 / 121 | — | **Event pool:** 87 user evidence turns contain an explicit calendar date. Each becomes a **single-hop** event item ("When did I get my car serviced for the first time?" → *March 15*). Take 50. |
| *_abs (abstention) | 30 | — | Template for our **15 unanswerable controls** |

**LoCoMo is not used for the main set.** Its dialogues are between two people talking about each other ("When did Caroline…"), which doesn't fit our setting of a user telling an assistant about themselves. It's also CC BY-NC. It stays as a backup event source only.

### 3.2 Item eligibility filter (apply in Phase 3) [DECIDED]
Keep an item only if **all** of these hold:
1. Answerable from **one** user turn (single hop).
2. The answer is a **short slot** (≤ 6 words), not an open-ended description.
3. It can't be answered from world knowledge alone (it's personal to the user).
4. It translates naturally into Hindi (drop US-specific idioms, sports, units that need conversion).
5. It's unambiguous with no time context (events carry an explicit date in the text).
6. It's balanced: at most 5 items per topic cluster (cars, travel, fitness…), so no single topic dominates.

### 3.3 Item content (per item, in each of EN / HI / HG)
| Field | Description |
|---|---|
| `memory_turn` | The user turn that states the memory (rewritten to ≤ 60 words, keeping the original wording where possible) |
| `assistant_reply` | A short assistant reply (≤ 50 words) that doesn't repeat the slot value |
| `followup_turn` + reply | One more on-topic user/assistant exchange in the same session, with no slot value |
| `q1`, `q2` | Two equivalent direct query paraphrases |
| `q3` | Indirect query [ABLATION subset] ("I'm planning my week. How much time should I keep for travelling to work each day?") |
| `gold.slots` | Slot values with **aliases in EN, Devanagari and Roman** (e.g., `["45 minutes","45 मिनट","45 minute","45 min"]`) |
| `distractor` | (30% of items) A near-miss statement in the same language: **referent swap with a different value** ("my *sister's* commute is only 20 minutes"). It's appended as a sentence to the first user turn of a filler session. If the model gives the distractor value, that's the detectable wrong answer. |

**Abstention controls (15, 5 per type):** the queried detail never appears, but a related one does. ("What car do I drive?" when only a car *service* was mentioned.) Correct = the model says it doesn't know or doesn't have that information.

The full JSON schema with one worked item is in `phase2/item_schema_example.json`.

### 3.4 Translation & verification protocol [DECIDED]
1. **Draft:** EN → HI and EN → HG, machine-drafted (any strong LLM). Record the model name.
2. **Verify:** each item is checked independently by **2 of 3 team members**. Checklist: (a) same meaning, (b) slot value unchanged, (c) natural register, (d) follows conventions §2.1–2.2, (e) query paraphrases are equivalent.
3. **Log:** for every item, record ACCEPT / EDIT / REJECT per annotator and the edit distance. Report **% accepted unedited** and **inter-annotator agreement (Cohen's κ on ACCEPT vs not)**.
4. **Resolve** disagreements by discussion. If still unresolved, **drop the item** and replace it from the pool.

### 3.5 Conversation histories (haystacks) [DECIDED]
- **Filler pool:** **40 non-evidence sessions** from LongMemEval-S haystacks.
  - Trim each to 2 user + 2 assistant turns, with assistant turns cut to ≤ 80 words.
  - Machine-translate once to HI and HG with the fixed translator (§4.3).
  - **Spot-check 10%** (not fully verified: filler isn't scored).
  - Drop any filler that mentions any item's slot value.
- **Filler language = storage language.** The whole history is in L_s, so a Hindi memory doesn't stand out against English filler. That's a salience confound we avoid. (MLNeedle found haystack language matters little, so this costs nothing and is more realistic.)
- **Main length (Short):** 1 evidence session + **9 filler sessions** = 10 sessions.
- **[ABLATION] Long:** 1 evidence + **29 filler** = 30 sessions, on a 60-item subset.
- **Evidence position:** slot 2, 5 or 9 of 10 (early / middle / late), assigned in a balanced way within each memory type, and **identical across all language conditions** for that item. This controls lost-in-the-middle effects.
- **Filler sampling:** a fixed random seed per item, identical across conditions. **The only thing that differs between conditions is the language.**
- **Distractor placement:** in a filler session at least 2 sessions away from the evidence.
- **Query:** a new final session containing only the query in L_q.
- **[CHECK IN PHASE 4]** Hindi and Hinglish produce more tokens than English for the same content. Measure tokens per condition for both tokenizers, confirm every prompt fits the context window (Long ≤ 28k tokens), and **report token counts per language**. This token difference is part of the real-world effect, not something to remove.

---

## 4. Memory setups (independent variable 3)

### 4.1 Setups [DECIDED]
| ID | Setup | What the reader sees |
|---|---|---|
| **FC** | Full context | The whole history (10 sessions) + the query |
| **RM-S1** | Retrieval, **original** | Top-5 retrieved past user turns, as originally written + the query |
| **RM-S2** | Retrieval, **English pivot** | Memories indexed as English translations. **The query is also translated to English for retrieval.** The reader gets the top-5 English memories + the original query. |
| **RM-S3** | Retrieval, **dual** | Index holds the original *and* English translation of each turn. Retrieve with the original query over both, merge duplicates by turn ID. The reader gets the top-5 turns, each shown as original + English. |
| **OR-S1/S2/S3** | **Oracle** | The gold evidence turn only (+ the distractor turn, if the item has one), in the S1/S2/S3 representation + the query |

- **Memory unit:** one **user turn** (memories are things the user disclosed). Assistant turns aren't indexed.
- **Index size per item:** 20 user turns (10 sessions × 2).

### 4.2 Retrieval [DECIDED]
- **Main retriever:** **BGE-M3**, dense, cosine similarity, **top-k = 5**.
- **Recall reporting:** R@1, R@3, R@5, R@10.
- **Retrieval-only baselines** (recall only, not passed to readers):
  - **BM25** (lexical; expected to collapse cross-lingually)
  - **multilingual-E5-large** (second dense model, robustness)

### 4.3 Translation inside the system (S2, S3) [DECIDED]
- **Fixed translator for both readers:** **Qwen3-8B**, greedy, with a fixed prompt "Translate to English. Output only the translation."
- Because the translator is fixed, the S2/S3 index is **identical for both readers**, so recall is reader-independent.
- All translations are cached.
- **Spot-check 10% of evidence-turn translations** and report how often the slot value survives translation. This separates "the translation broke it" from "the retrieval or reading broke it".

---

## 5. Readers, prompting, compute

### 5.1 Readers [DECIDED]
| Reader | Why | Notes |
|---|---|---|
| **Qwen3-8B** | Open weights (Apache-2.0); vendor reports 119 languages and dialects incl. Hindi | Thinking mode **off** (`enable_thinking=False`) |
| **Llama-3.1-8B-Instruct** | Hindi is one of its 8 officially supported languages | Gated on HF: accept the licence early |
| *[OPTIONAL]* Aya-Expanse-8B or a free-tier API model | Indic / stronger reference point | Only if compute allows |

**Decoding:** greedy (temperature 0), `max_new_tokens = 96`, fp16, **the same precision for every condition**.

### 5.2 Prompt [DECIDED]
**The system prompt is always in English, in every condition.** That way only the language of the memory and the query varies. Exact templates are in Appendix A.

The reader is told to answer briefly, in the **language of the question**, and to say it doesn't know if the information isn't in its memory.

### 5.3 Compute (free tier) [CHECK IN PHASE 4]
- **Platform:** Kaggle **2× T4** with vLLM, tensor-parallel = 2, fp16. An 8B model in fp16 needs about 16 GB, so it **doesn't fit on one T4** without quantization.
- **Prefix caching on:** the same history is reused across 3 query languages × 2 paraphrases.
- **Rough estimate:** about **3 GPU-hours per reader** for the main grid, plus about 2 for the judge, plus ablations.
  - Kaggle gives **30 h/week per account** (3 accounts = 90 h).
  - Some sources say 2× T4 uses up quota twice as fast. Even then this fits.
  - These numbers are estimates; we time them on the pilot.
- **Colab fallback:** a 4-bit AWQ model on one T4. If we use it, it's used for **all** conditions of that reader.

---

## 6. Evaluation

### 6.1 Metrics [DECIDED]
| Metric | Definition | Source |
|---|---|---|
| **Accuracy (primary)** | Correct per §2.4; abstention items are correct if the model says it doesn't know | LLM judge |
| **Slot match** | All gold slots found (after normalization: lowercase, Unicode NFC, strip punctuation, alias list across scripts, digits normalized) | Deterministic |
| **Recall@k** | The gold evidence turn is in the top-k | Retrieval logs |
| **Reading accuracy** | Accuracy restricted to items where the gold turn is in the top-5 | Derived |
| **Distractor capture** | The response contains the distractor value | Deterministic |
| **False abstention** | Answerable item, but the model says it doesn't know | Judge + regex |
| **Hallucination on controls** | Unanswerable item, but the model gives a specific answer | Judge |
| **Response language** | Devanagari / Latin-Hindi / English, from script ratio + a word list | Deterministic |
| **Translation slot survival** | The slot value survives in the S2 translation | Deterministic + spot check |

### 6.2 LLM judge [DECIDED]
- **Judge:** **Qwen3-14B**, 4-bit, thinking off.
- **Input:** question, gold answer with aliases (all 3 scripts), and the response. **Output:** `CORRECT`, `INCORRECT` or `NO_ANSWER`.
- **Validation:** humans label **200 responses**, stratified by cell × reader. We report **Cohen's κ** per reader, which also checks whether the judge favours the Qwen reader because it's the same family.
- **Rule:** if κ ≥ 0.80, use the judge as is. Otherwise revise the judge prompt once. If it's still below 0.80, **slot match becomes the primary metric**, and judge/slot disagreements get human adjudication.

### 6.3 Error taxonomy (on ~150 sampled errors, stratified) [DECIDED]
| Code | Error | Detected |
|---|---|---|
| E1 | **Entity substitution:** a different entity than the gold | manual |
| E2 | **Number / date altered** | slot + manual |
| E3 | **Polarity or preference inversion** | manual |
| E4 | **Distractor capture** | automatic |
| E5 | **Transliteration corruption:** the right entity, garbled across scripts | manual |
| E6 | **False abstention** | automatic |
| E7 | **Unsupported content** (hallucination) | manual |
| E8 | **Partial:** some slots missing | slot |

Two annotators label 50 errors together (report κ), then split the rest.

---

## 7. Experiment matrix

| Block | Items | Cells | Setups | Queries | Readers | Generations |
|---|---|---|---|---|---|---|
| **Main** (Short) | 165 (150 + 15 controls) | 9 | 7 (FC, RM-S1/2/3, OR-S1/2/3) | q1, q2 | 2 | **41,580** |
| **[ABLATION]** Long haystack | 60 | 9 | FC, RM-S1, RM-S3 | q1 | 2 | 3,240 |
| **[ABLATION]** Indirect query | 50 | 9 | FC, RM-S1/2/3 | q3 | 2 | 3,600 |
| **[ABLATION]** Devanagari digits | 50 events | HI storage × 3 query langs | FC, RM-S1/2/3 | q1 | 2 | 1,200 |
| **[OPTIONAL]** English-framed Hinglish | 50 | HG storage × 3 | FC, RM-S1 | q1 | 2 | 600 |
| **[OPTIONAL]** Write stage: LLM-extracted memory notes instead of raw turns | 50 | 9 | RM-S1 | q1 | 1 | 450 |

**Retrieval-only runs** (BGE-M3, BM25, mE5 × S1/S2/S3 × 9 cells) need no GPU generation.

---

## 8. Pilot (Phase 5) decision rules [DECIDED]
Pilot = 30 items, both readers, all 9 cells, FC + RM-S1 + OR-S1.

| Pilot observation | Action |
|---|---|
| Monolingual EN ≥ 95% **and** all cross-lingual cells ≥ 92% (ceiling effect) | Use **Long** as the main length and raise distractors to 50% of items |
| Monolingual EN < 70% | Assume a bug (prompt, parsing, judge). Fix it before any main run. |
| Judge κ < 0.80 on the pilot labels | Revise the judge prompt (§6.2) |
| Verification REJECT rate > 15% | Tighten the translation guidelines, re-brief annotators |
| Any prompt > context limit | Shorten the filler (trim assistant turns to ≤ 50 words) |

---

## 9. Threats to validity (and what we do about them)
| Threat | Mitigation |
|---|---|
| Translation changes meaning | 2-annotator verification, slot-preservation check, report agreement |
| Hindi and Hinglish use more tokens (a longer effective context) | Report token counts per language. Length ablation. Fixed sessions per history. |
| Answer depends on world knowledge, not memory | Eligibility rule 3. The oracle vs FC comparison. Unanswerable controls. |
| The judge is weak in Hindi or favours its own model family | Human validation per reader. Slot-match fallback. |
| A Western-centric source makes the content unnatural for Hindi | Eligibility rule 4. Native-speaker editing. Noted as a limitation. |
| Only 8B open models | Stated scope. An optional stronger API reader. |
| Hinglish spelling isn't standardized | Fixed spelling sheet. Spelling variation is future work. |
| Data contamination (LongMemEval is public) | Items are rewritten and translated. The memory is personal (not world knowledge). Oracle/FC results check this. |
| Researcher degrees of freedom | This spec is frozen. Deviations logged. All conditions run, all reported. |

---

## 10. Repository layout [DECIDED]
```
Cross-Lingual-Memory-Project/
├── phase1/                 literature review, references.bib
├── phase2/                 this spec, item schema, power analysis, DEVIATIONS.md
├── data/
│   ├── raw/                longmemeval_oracle.json, locomo10.json (downloaded 2 Oct 2026)
│   ├── items/              items_v1.jsonl (Phase 3 output, frozen 19 Oct)
│   └── haystacks/          generated histories per item × storage language
├── src/                    memory.py, retrieve.py, run.py, judge.py, evaluate.py
├── results/                raw generations (jsonl, cached), scores, tables
└── report/                 midsem + final report
```

---

## Appendix A — Prompt templates [DECIDED]

**A.1 Reader (FC)**
```
SYSTEM: You are a personal assistant with memory of your past conversations with this user.
Answer the user's question using only what the user told you in past conversations.
Answer in one short sentence, in the same language as the question.
If the information is not in the past conversations, say that you don't know.

USER: Past conversations:
[Session 1]
User: ...
Assistant: ...
...
[Session 10]
...

Current question: {query}
```

**A.2 Reader (RM / OR)** — same system prompt; the user message is:
```
Relevant memories from past conversations (may be incomplete or irrelevant):
1. {memory_1}
...
5. {memory_5}

Current question: {query}
```
For S3, each memory is shown as `{original} (English: {translation})`.

**A.3 Judge**
```
You are grading an assistant's answer about a user's personal information.
Question: {query}
Gold answer: {gold_en}   Accepted forms: {aliases}
Assistant answer: {response}
The answer may be in English, Hindi (Devanagari) or Hinglish (romanized). Judge meaning, not language.
Reply with exactly one word:
CORRECT - states the gold information without contradiction
INCORRECT - wrong, incomplete, lists several candidates, or contradicts the gold
NO_ANSWER - says it does not know / has no information
```

**A.4 Translator (S2/S3)**
```
Translate the following text to English. It may be Hindi, Hinglish (romanized Hindi) or English.
Keep names, numbers and dates exactly. Output only the translation.
Text: {text}
```
