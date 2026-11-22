# Phase 1 — Literature Review & Positioning
**Project:** Cross-Lingual Memory in LLM Agents
**Status:** done 2 Oct 2026 · citations in `references.bib` (BibTeX keys in `[brackets]` below)

> **How this was verified.** Every title, author list, year and arXiv ID was pulled from the arXiv API. Venues were checked against ACL Anthology / Semantic Scholar. For the 6 papers closest to us, the claims below come from the paper text itself, not just the abstract. 4 bib entries still carry a `VERIFY` note (PHINC venue; main vs. Findings track for two ACL papers).

---

## 1. Bottom line (one paragraph)

Memory benchmarks for LLM agents (LongMemEval, LoCoMo, MemoryAgentBench, AMA-Bench) are effectively **monolingual English**. Cross-lingual work (MLQA, MLNeedle, XRAG, XBCP) is about **documents or Wikipedia passages, not personal user memory**. Most of it **fixes the question language to English**. None of it tests **romanized Hindi–English code-mixing**, and none compares **how the memory should be stored**. The one memory resource that mixes languages, the EN/VI dataset our proposal cites, assigns each probe **one language only**: it has no matched counterpart, so you can't tell whether an error comes from the language switch. **No work we found crosses storage language × query language over the *same* personal memories, includes Hinglish, and compares original / translated / dual storage.** MLQA's "G-XLT" setting (question and context in different languages, parallel content) is the closest design ancestor. Our project brings that controlled design to **agent memory**.

---

## 2. Comparison table (goes into the report)

Legend: ✓ yes · ✗ no · ◐ partial · — not applicable

| Work | Personal / agent memory | Varies storage lang. | Varies query lang. independently | Same content across langs (matched) | Hindi | Romanized code-mix (Hinglish) | Compares memory representations | Separates retrieval vs reading failure |
|---|---|---|---|---|---|---|---|---|
| LongMemEval [wu2025longmemeval] | ✓ | ✗ | ✗ | — | ✗ | ✗ | ◐ (EN only) | ✓ (index / retrieve / read) |
| LoCoMo [maharana2024locomo] | ✓ | ✗ | ✗ | — | ✗ | ✗ | ◐ (EN only) | ✗ |
| MemoryAgentBench [hu2026memoryagentbench] | ✓ | ✗ | ✗ | — | ✗ | ✗ | ◐ (agent types, EN) | ✗ |
| EN/VI long-horizon memory set [nguyendang2026lhmemory] | ✓ | ◐ (mixed per event) | ◐ (per probe) | **✗** | ✗ | ✗ (EN–VI) | ✗ | ✗ |
| Wontopos Tablet 2 [kim2026wontopos] | ✓ (one product) | ✓ (photo captions) | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| MLQA G-XLT [lewis2020mlqa] | ✗ (Wikipedia QA) | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| MLNeedle [hengle2025mlneedle] | ✗ (Wikipedia QA) | ✓ | **✗ (always EN)** | ✓ | ✓ | ✗ | ✗ | ✗ |
| XRAG [liu2025xrag] | ✗ (news RAG) | ◐ | ✓ | ◐ | ✗ | ✗ | ✗ | ✗ |
| XBCP [lu2026xbcp] | ✗ (web research) | ✓ | **✗ (always EN)** | ✓ (translated) | ✗ | ✗ | ✗ | ✓ (oracle) |
| Policy retention [mukherjee2026policyretention] | ✗ (tool policy) | — | ✓ | ✓ | ? (41 langs; Hindi not checked) | ✗ | ✗ | ✗ |
| **Ours** | **✓** | **✓** | **✓** | **✓** | **✓** | **✓** | **✓** | **✓** |

**The point to make to the prof:** no prior row has ✓ in the four right-hand columns together with personal memory. That's the gap.

---

## 3. Gap statement (paste-ready)

> Existing long-term memory benchmarks evaluate whether an agent retains and retrieves user information over time, but they are built almost entirely in English (LongMemEval, LoCoMo, MemoryAgentBench). Cross-lingual evaluation has matured for question answering and retrieval-augmented generation (MLQA, MLNeedle, XRAG, XBCP), but there the "memory" is a Wikipedia passage, news article or web document rather than information the user disclosed about themselves, and the question is often fixed to English. Recent bilingual memory data mixes languages within trajectories, but each probe exists in only one language, so a failure cannot be attributed to the language switch itself. We close this gap with a controlled design: the underlying personal fact, preference or event is held fixed while the storage language and query language are varied independently across English, Hindi (Devanagari) and romanized Hinglish. We further test which memory representation (original, translated to English, or both) best survives the switch, and we separate retrieval failures from reading failures with an oracle condition.

---

## 4. Annotated bibliography

Each entry: **what it does → what we take from it → how we differ.** ★ = read the full paper.

### A. Long-term memory in LLM agents

**★ LongMemEval** [wu2025longmemeval] — ICLR 2025
- 500 questions inside scalable user–assistant chat histories. Tests 5 abilities: information extraction, multi-session reasoning, temporal reasoning, knowledge updates, abstention. Commercial assistants and long-context LLMs drop about **30%** on sustained interactions. Proposes a **3-stage framework: indexing → retrieval → reading.**
- **Take:** our candidate source items. The 3-stage framework is the backbone of our write → store → retrieve → read diagnosis; cite it as the origin.
- **Differ:** English only. Never varies the language of the memory or the question.

**★ LoCoMo** [maharana2024locomo] — ACL 2024
- Very long conversations (~300 turns, ~9K tokens, up to 35 sessions), generated by LLM agents and human-verified. QA categories: single-hop, multi-hop, temporal, open-domain. Long-context and RAG help, but stay well below humans.
- **Take:** an alternative source of facts and events. Its machine-generate-then-human-verify pipeline justifies our LLM-draft + 2-person verification protocol.
- **Differ:** English only.

**MemGPT** [packer2023memgpt] — arXiv 2023
- Treats the context window as an OS-style memory hierarchy: the agent pages information between main context and external storage.
- **Take:** motivation for *explicit* memory stores. Our "retrieval memory" setup is a minimal version of this.
- **Differ:** an architecture, not an evaluation. No multilingual angle.

**Beyond Goldfish Memory (MSC)** [xu2022goldfish] — ACL 2022
- Multi-Session Chat dataset: an early long-term open-domain dialogue benchmark. Retrieval and summarization of past sessions beat plain context.
- **Take:** historical anchor for "memory across sessions." One sentence in related work.

**MemoryBank** [zhong2024memorybank] — AAAI 2024 · **Mem0** [chhikara2025mem0] — ECAI 2025 · **A-MEM** [xu2025amem] — NeurIPS 2025
- Practical memory systems: extract and store memory notes, retrieve by embedding, update or forget.
- **Take:** our **S1/S2/S3 strategies are choices *inside* such a system** (what text the note holds). Frame RQ4 as "a design decision every memory system makes implicitly."
- **Differ:** all evaluated on English benchmarks.

**MemoryAgentBench** [hu2026memoryagentbench] — ICLR 2026
- 4 competencies: accurate retrieval, test-time learning, long-range understanding, selective forgetting. Compares context-based, RAG and external-memory agents.
- **Take:** our setups (full-context vs retrieval) mirror their agent types. Our target competency is **accurate retrieval**.

**AMA-Bench** [zhao2026amabench] — arXiv 2026
- Long-horizon memory for agentic (environment-interaction) tasks. Finds similarity-based retrieval misses causal and objective information.
- **Take:** one of the three sources behind the EN/VI dataset. Cite in passing.

**Surveys:** [zhang2024memorysurvey], [du2025rethinkingmemory]. Use them for one sentence of taxonomy (short- vs long-term, memory operations). Neither covers cross-lingual memory, which is worth saying explicitly.

**★ EN/VI long-horizon agent-memory dataset** [nguyendang2026lhmemory] — HF, created 26 Jun 2026 (**the "example resource" in our proposal**)
- 40 cases (15 AMA-Bench, 15 LongMemEval, 10 LoCoMo), 288 probe stages, field-level ground truth, failure tags.
- **What we measured ourselves:** of 1,411 events, **1,086 EN (77%), 189 VI (13%), 136 mixed EN+VI (10%)**. Of 288 probes, 217 are in VI and 71 in EN. **Each probe exists in only one language. There is no parallel version.**
- **Differ (key argument):** it shows language switching matters for memory, but it can't isolate the effect of the switch. Accuracy differences across probes mix language effects with question difficulty. Our matched design removes that confound. Also EN–VI, not Hindi/Hinglish.

**Wontopos Tablet 2** [kim2026wontopos] — arXiv, Aug 2026, single author, about a production memory engine
- Text memory results are on English benchmarks (LongMemEval-S, BEAM). Its cross-lingual part is a **store-language × query-language grid (70 cells, 14 languages incl. Hindi) over synthetic photographs with captions**. Lexical BM25 collapses cross-lingually; dense embedders vary hugely by language.
- **Take:** independent evidence that the store × query grid reveals large language effects in memory retrieval. It supports our H1.
- **Differ:** images and captions, not personal facts, preferences or events. One proprietary engine. No code-switching. No reading or generation analysis. No representation comparison. **Cite it honestly, as the closest "grid" precedent.**

### B. Cross-lingual QA, long context, RAG and agents

**★ MLQA** [lewis2020mlqa] — ACL 2020
- Parallel extractive QA in 7 languages (EN, AR, DE, ES, **HI**, VI, ZH). Defines **G-XLT: the question in language *y*, the context in language *z***, possible because the data is parallel. Result: models do best when context and question languages match, *except for Hindi and Arabic*.
- **Take:** **the design ancestor of our 3×3 grid.** Cite it as such; it makes the method look grounded rather than invented.
- **Differ:** short Wikipedia paragraphs, fine-tuned encoder readers, no memory, no code-mixing.

**★ MLNeedle** [hengle2025mlneedle] — NAACL 2025 (IIT Delhi)
- Needle-in-a-haystack built on MLQA. Varies needle language, haystack language and needle position across 7 languages incl. Hindi. Performance is lowest when the needle is outside the English language family and in the middle of the context. Models care more about the needle's language than the haystack's.
- **The detail that matters most for us (from §2.1 of the paper):** *"The language of the question is kept fixed in English."*
- **Take:** strong prior evidence for H1/H2. Their "haystack language barely matters" result tells us we can **fix the filler language** without hurting validity.
- **Differ:** the query language never changes, the content isn't personal memory, and there's no code-mixing and no memory store or representation.

**XRAG** [liu2025xrag] — Findings of EMNLP 2025
- Cross-lingual RAG on news in EN, DE, ES, ZH, AR (**no Hindi**). Two findings: (1) with English-only retrieval, models often answer in the **wrong language**; (2) with mixed-language retrieval, the hard part is **reasoning across languages**, not generating non-English text.
- **Take:** add "response language" as a secondary logged variable, and a distortion type ("answered in wrong language").

**Multilingual RAG baseline** [chirkova2024mrag] — KnowLLM @ ACL 2024
- RAG with queries and datastore in 13 languages. Needs prompt engineering to answer in the user's language. **Metrics must tolerate spelling variants of named entities.** Lists frequent code-switching in non-Latin-script languages as an open problem.
- **Take:** justification for our **slot checker with transliteration normalization** (e.g., *Pune / पुणे / Poona*).

**★ XBCP — Cross-lingual BrowseComp-Plus** [lu2026xbcp] — arXiv, Jun 2026
- Keeps English questions and answers, translates the supporting evidence into 12 languages (**no Hindi**). Dense retrievers lose evidence recall. Crucially, **even with oracle evidence, accuracy stays below the original** (e.g., GPT-OSS-120B: 94.7% original vs 85.3% cross-lingual oracle). A fully target-language prompt did *worse*.
- **Take:** **direct precedent for our oracle condition** and for splitting failures into retrieval vs reading. Their result predicts that our oracle cells will still drop.
- **Differ:** web documents, query fixed to English, no code-mixing, no comparison of storage representations (they don't test translating evidence back to English, which is our S2).

**Cross-lingual context retrieval** [gao2025xlcontextretrieval] — EMNLP 2025
- Cross-lingual machine reading has two internal phases, question encoding and answer retrieval. The bottleneck is in the last layers of the second phase.
- **Take:** one-sentence mechanistic background for why reading can fail even when retrieval succeeds.

**Cross-lingual policy retention** [mukherjee2026policyretention] — COLM 2026 (Microsoft Research India)
- The same tool-use tasks in 41 languages: frontier models keep only about **71–73%** of their action policy. **Models route non-English tasks through English, and the pivot is causally load-bearing.** Warns about measurement confounds (empty or short traces, chance agreement, run-to-run noise).
- **Take:** (1) supports H2 (an English pivot makes directions asymmetric); (2) **methodological warning**: measure the *same-language* noise floor (run the monolingual cells twice) before calling a gap real.
- **Differ:** about action policy, not memory recall. No code-mixing.

**Do Llamas Work in English?** [wendler2024llamas] — ACL 2024 · **Self-translate** [etxaniz2024selftranslate] — NAACL 2024
- Llama-2's internal "concept space" sits closer to English. Translating non-English input into English (even with the model itself) beats direct inference.
- **Take:** the theory behind **H2** (asymmetry) and **S2** (translate memories to English) as a sensible strategy.

**Cross-lingual factual consistency (RankC)** [qi2023rankc] — EMNLP 2023 (Outstanding Paper)
- The same fact isn't consistently known across languages, and model size doesn't fix it. Facts edited in English transfer only to "similar" languages.
- **Take:** the *parametric-knowledge* version of our question. We study *in-context / stored* user knowledge. One-line contrast in related work.

**Lost in the Middle** [liu2024lostinthemiddle] — TACL 2024
- Accuracy drops when relevant information is in the middle of a long context.
- **Take:** **control memory position** in the haystack (fix it or balance it); otherwise position is a confound.

### C. Code-switching and Hinglish

**GLUECoS** [khanuja2020gluecos] — ACL 2020 · **LinCE** [aguilar2020lince] — LREC 2020
- Standard code-switching benchmarks. Both include Hindi–English. Classic tasks (LID, NER, POS, sentiment, QA, NLI).
- **Take:** cite them to establish Hinglish as an established, studied variety, and that prior code-switching evaluation never addressed memory.

**Lost in the Mix** [mohamed2025lostinthemix] — ACL 2025
- Builds code-switched variants of reasoning benchmarks. Inserting foreign tokens into English hurts comprehension; embedding English into another language often *helps*.
- **Take:** a concrete prediction for **H3**: Hinglish with a Hindi base and English insertions may hurt less than expected. That's an interesting result either way.

**OLA** [oh2026ola] — ACL 2026
- When users code-switch, LLMs often pick the wrong response language and switch mid-response.
- **Take:** log response language for HG queries.

**PingPong** [farhansyah2026pingpong] — arXiv 2026
- Human-written multi-party code-switching dialogues; replies often refer back to much earlier turns. LLMs are weak on its QA.
- **Take:** shows code-switched *long* dialogue is hard. **Differ:** no Hindi, not memory storage or retrieval, not a controlled language swap.

**Language anchoring** [park2026anchoring] — Findings of EMNLP 2026
- Code-switched hidden states anchor to the grammatical frame language. Target-framed code-switching degrades QA more.
- **Take:** suggests a cheap ablation: **Hindi-framed vs English-framed Hinglish**.

**IndicTalk** [gawande2026indictalk] — arXiv 2026
- Persona-based conversational corpus, 9 Indic languages, native + romanized scripts, code-mixing.
- **Take:** possible source of **realistic Hinglish filler turns** for haystacks. **Differ:** no cross-session memory evaluation.

**PHINC** [srivastava2020phinc] — W-NUT 2020 (venue to verify)
- Parallel Hinglish ↔ English sentences from social media.
- **Take:** a style reference for natural romanized Hinglish when we write the HG variants.

### D. Tools (method citations)
- **BGE-M3** [chen2024bgem3] — multilingual dense embedder (main retriever).
- **multilingual-E5** [wang2024me5] — second embedder for robustness.
- **LaBSE** [feng2022labse] — optional sentence-similarity metric for "semantic distortion".
- **IndicTrans2** [gala2023indictrans2] — EN↔HI translation for S2 and for drafting HI variants.

---

## 5. Design decisions Phase 1 led to (feeds Phase 2)

| # | Decision | Because of |
|---|---|---|
| 1 | Frame the 3×3 grid as **"G-XLT for agent memory"** | MLQA |
| 2 | Keep the **oracle condition**; expect oracle cells to drop too | XBCP, Gao et al. |
| 3 | **Fix filler language** and **control memory position** | MLNeedle (haystack language matters little), Lost in the Middle |
| 4 | Slot checker with **transliteration and spelling normalization** | Chirkova et al. |
| 5 | Log **response language** as a secondary outcome; add "wrong-language answer" to distortion types | XRAG, OLA |
| 6 | **Run monolingual cells twice** to measure the noise floor before claiming gaps | Mukherjee et al. |
| 7 | Optional ablation: **Hindi-framed vs English-framed Hinglish** | Lost in the Mix, Park et al. |
| 8 | Source items from **LongMemEval / LoCoMo** (MIT / CC BY-NC respectively) | licences listed in the EN/VI dataset card |

## 6. Hypotheses, now grounded in literature

- **H1** (cross-lingual drop): MLNeedle, XBCP, Wontopos grid.
- **H2** (asymmetry, English-side advantage): Wendler et al., Etxaniz et al., Mukherjee et al.
- **H3** (Hinglish hardest): Chirkova et al. (spelling variants), PingPong. **Counter-evidence:** Lost in the Mix (English inserted into another language can help). Present H3 as an open question; that's more honest and more interesting.
- **H4** (dual storage best; English pivot good but lossy on names and numbers): self-translate supports S2. Chirkova et al. on entity spelling suggests S2's weakness.

---

## 7. Related work — report-ready draft (~650 words)

> **Long-term memory in LLM agents.** Early work on multi-session dialogue showed that conversational agents benefit from retrieving or summarizing earlier sessions rather than relying on a fixed context window (Xu et al., 2022). MemGPT (Packer et al., 2023) framed memory as an explicitly managed resource, and systems such as MemoryBank (Zhong et al., 2024), Mem0 (Chhikara et al., 2025) and A-MEM (Xu et al., 2025) extract, store, retrieve and update memory notes outside the model. Evaluation has kept pace: LoCoMo (Maharana et al., 2024) tests question answering over very long multi-session conversations, LongMemEval (Wu et al., 2025) measures five memory abilities and decomposes memory systems into indexing, retrieval and reading stages, and MemoryAgentBench (Hu et al., 2026) evaluates memory agents over incremental multi-turn input. These benchmarks are, however, constructed in English, and they do not ask whether a memory survives when the user changes language between storing and recalling it.
>
> **Cross-lingual retrieval and reading.** The closest methodological precedent is MLQA (Lewis et al., 2020), whose generalized cross-lingual transfer setting pairs a question in one language with a context in another over parallel data, and finds that matched languages generally perform best. MLNeedle (Hengle et al., 2025) extends this to long contexts and shows that LLMs struggle most when the relevant passage is in a non-English-family language, although the question is kept in English. In retrieval-augmented generation, XRAG (Liu et al., 2025) reports that models often answer in the wrong language and struggle to reason over mixed-language evidence, and Chirkova et al. (2024) note that evaluation must tolerate spelling variation in named entities. Most recently, XBCP (Lu et al., 2026) translates the evidence for English research questions into twelve languages and finds that accuracy drops even when gold evidence is supplied directly, pointing to a reading bottleneck independent of retrieval. Analyses of model internals suggest one reason: multilingual LLMs process meaning in a space closer to English (Wendler et al., 2024), and translating inputs to English often helps (Etxaniz et al., 2024). In agentic settings, Mukherjee et al. (2026) show that tool-using agents retain only part of their action policy across languages and route non-English tasks through English. All of this work concerns documents, passages or task policies rather than personal information that the user disclosed earlier.
>
> **Code-switching.** Hindi–English code-mixing (Hinglish) is well established in NLP benchmarks such as GLUECoS (Khanuja et al., 2020) and LinCE (Aguilar et al., 2020). Recent studies find that LLM comprehension degrades on code-switched input in ways that depend on which language provides the grammatical frame (Mohamed et al., 2025; Park et al., 2026), and that models misjudge which language to answer in (Oh et al., 2026). PingPong (Farhansyah et al., 2026) shows that long, multi-party code-switched dialogue remains difficult. None of these works evaluates memory storage and retrieval.
>
> **Multilingual memory.** Language mixing has only recently entered memory evaluation. A bilingual English–Vietnamese long-horizon memory dataset (Nguyen Dang, 2026) mixes languages across events and probes, but each probe appears in a single language, so the effect of the language switch cannot be separated from item difficulty. Kim (2026) evaluates a production memory engine over a grid of storage and query languages, but for captioned photographs rather than personal facts, and without code-switching. **Our work differs** in holding the underlying personal fact, preference or event fixed while independently varying storage and query language across English, Hindi and romanized Hinglish; in comparing original, translated and dual memory representations; and in separating retrieval from reading failures with an oracle condition.

*(Convert the author-year mentions to `\citet{}`/`\citep{}` with the keys in `references.bib`.)*

---

## 8. Remaining Phase 1 tasks (team, ~1 day)

- [ ] **Full read (★), split across the 3 of you:** LongMemEval, LoCoMo, MLQA (§3 and §5.2 only), MLNeedle, XBCP, the EN/VI dataset (open `cases.jsonl` and look at 2–3 cases). Check every claim in §4 against the paper. If anything is off, fix it here.
- [ ] Resolve the 4 `VERIFY` notes in `references.bib`.
- [ ] Check the LongMemEval and LoCoMo GitHub repos: data format, licence (MIT vs CC BY-NC 4.0), and how easy it is to extract single-fact items. This feeds Phase 3.
- [ ] Put the comparison table (§2) and related work (§7) into the midsem report.
