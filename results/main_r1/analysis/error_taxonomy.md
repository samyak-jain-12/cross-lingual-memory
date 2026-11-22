# Error taxonomy on `main_r1` (150 sampled errors)

Stratified sample of answerable responses judged not CORRECT (reader × FC/RM/OR × mono/cross; 12–13 each, one error per item per stratum). E4 and E6 are automatic unless overridden; the rest were labelled by hand by one annotator (Claude, an AI assistant), so no inter-annotator agreement is reported. *Weighted* re-weights each stratum to its share of all 2,386 errors.

| code | error | n | raw | weighted |
|---|---|---|---|---|
| E1 | entity substitution | 14 | 9% | 9% |
| E2 | number / date altered | 6 | 4% | 4% |
| E3 | polarity / preference inversion | 1 | 1% | 0% |
| E4 | distractor capture | 31 | 21% | 19% |
| E5 | transliteration corruption | 5 | 3% | 3% |
| E6 | false abstention | 62 | 41% | 48% |
| E7 | unsupported content | 6 | 4% | 4% |
| E8 | partial answer | 2 | 1% | 1% |
| E9 | off-task / degenerate output | 15 | 10% | 8% |
| OK | actually correct (judge false negative) | 8 | 5% | 5% |

### By mono vs cross-lingual cells (weighted share within each column)

| code | cross (n=78) | mono (n=72) |
|---|---|---|
| E1 entity substitution | 7% | 13% |
| E2 number / date altered | 5% | 2% |
| E3 polarity / preference inversion | 1% | 0% |
| E4 distractor capture | 18% | 21% |
| E5 transliteration corruption | 3% | 2% |
| E6 false abstention | 53% | 33% |
| E7 unsupported content | 4% | 5% |
| E8 partial answer | 1% | 1% |
| E9 off-task / degenerate output | 4% | 17% |
| OK actually correct (judge false negative) | 4% | 6% |

### By setup group (weighted share within each column)

| code | FC (n=50) | OR (n=50) | RM (n=50) |
|---|---|---|---|
| E1 entity substitution | 4% | 12% | 13% |
| E2 number / date altered | 0% | 14% | 3% |
| E3 polarity / preference inversion | 0% | 2% | 0% |
| E4 distractor capture | 10% | 26% | 24% |
| E5 transliteration corruption | 4% | 1% | 4% |
| E6 false abstention | 66% | 26% | 39% |
| E7 unsupported content | 4% | 3% | 5% |
| E8 partial answer | 0% | 2% | 1% |
| E9 off-task / degenerate output | 11% | 6% | 4% |
| OK actually correct (judge false negative) | 2% | 9% | 6% |

### By reader (weighted share within each column)

| code | llama3.1-8b (n=75) | qwen3-8b (n=75) |
|---|---|---|
| E1 entity substitution | 2% | 14% |
| E2 number / date altered | 0% | 7% |
| E3 polarity / preference inversion | 1% | 0% |
| E4 distractor capture | 16% | 20% |
| E5 transliteration corruption | 5% | 2% |
| E6 false abstention | 65% | 35% |
| E7 unsupported content | 1% | 6% |
| E8 partial answer | 2% | 0% |
| E9 off-task / degenerate output | 4% | 10% |
| OK actually correct (judge false negative) | 5% | 5% |

### Notes

- Automatic codes overridden by hand: 1 (X123).
- E4/E6 cases the automatic flags missed (transliterated distractors, refusals not caught by the regex): 23.
- 8 of 150 sampled 'errors' are correct answers the judge rejected (e.g. नाइके = Nike, a correct ratio or count, or the gold plus extra advice).

