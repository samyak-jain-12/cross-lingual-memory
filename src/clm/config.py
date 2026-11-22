"""Fixed experimental settings. Values trace to phase2/design_spec.md (section in brackets)."""
import os
from pathlib import Path

# Data root: the project folder locally, /kaggle/working/clm on Kaggle (set CLM_ROOT).
ROOT = Path(os.environ.get("CLM_ROOT", Path(__file__).resolve().parents[2]))
DATA = ROOT / "data"
LANGS = ("en", "hi", "hg")                       # [2.1]
ALL_SETUPS = ("FC", "RM-S1", "RM-S2", "RM-S3", "OR-S1", "OR-S2", "OR-S3")   # [4.1]
TOP_K = 5                                        # [4.2]
RECALL_KS = (1, 3, 5, 10)                        # [4.2]
MAX_SESSIONS = 20                                # fillers are drawn for this length; shorter histories use a prefix
FILLER_POOL_SIZE = 40                            # [3.5]
# Evidence session slot for each position class, as a function of history length n.
# n=10 gives 2 / 5 / 9, exactly the pilot's slots; n=20 gives 4 / 10 / 19.
EVIDENCE_SLOT = {"early": lambda n: round(0.2 * n), "middle": lambda n: n // 2, "late": lambda n: n - 1}

# Experiment blocks [7] + ENDSEM_PLAN §1. Each block is run separately (CLM_BLOCK) and writes its own results
# folder; all blocks of one run share the English-translation cache. Item membership comes from flags set by
# src/merge_items.py. The pilot hit the ceiling rule (§8), so Long (20 sessions) is the main length and Short
# (10) is ablation A (DEVIATIONS #8).
BLOCKS = {
    "main":   {"sessions": 20, "qvs": ("q1", "q2"), "setups": ALL_SETUPS, "stores": LANGS, "flag": None, "digits": False},
    "short":  {"sessions": 10, "qvs": ("q1",), "setups": ("FC", "RM-S1", "RM-S3"), "stores": LANGS,
               "flag": "abl_short", "digits": False},
    "q3":     {"sessions": 20, "qvs": ("q3",), "setups": ("FC", "RM-S1", "RM-S2", "RM-S3"), "stores": LANGS,
               "flag": "abl_q3", "digits": False},
    "digits": {"sessions": 20, "qvs": ("q1",), "setups": ("FC", "RM-S1", "RM-S2", "RM-S3"), "stores": ("hi",),
               "flag": "abl_digits", "digits": True},   # Hindi histories written with Devanagari digits
}
BLOCK = os.environ.get("CLM_BLOCK", "main")
if BLOCK not in BLOCKS:
    raise ValueError(f"CLM_BLOCK must be one of {list(BLOCKS)}, got {BLOCK!r}")
_B = BLOCKS[BLOCK]

RUN_DIR = ROOT / "results" / os.environ.get("CLM_RUN", "pilot")
RESULTS = RUN_DIR if BLOCK == "main" else RUN_DIR / f"abl_{BLOCK}"
TRANSLATION_CACHE = RUN_DIR / "en_translations.json"     # shared by all blocks of a run

QUERY_VARIANTS = _B["qvs"]                       # [1.2] q1/q2 paraphrases; q3 = indirect (DEVIATIONS #7)
SETUPS = _B["setups"]
STORE_LANGS = _B["stores"]                       # storage languages built for this block (queries: all LANGS)
ITEM_FLAG = _B["flag"]
DEV_DIGITS = _B["digits"]
# Override with CLM_SESSIONS (the pilot r2 run used 10).
N_SESSIONS = int(os.environ.get("CLM_SESSIONS", _B["sessions"]))

MODELS = {                                       # [5.1], [4.3], [6.2]
    "qwen3-8b": "Qwen/Qwen3-8B",
    "llama3.1-8b": "meta-llama/Llama-3.1-8B-Instruct",
    "judge": "Qwen/Qwen3-14B-AWQ",
}
TRANSLATOR = "qwen3-8b"                          # [4.3] fixed translator for both readers
EMBEDDER = "BAAI/bge-m3"                         # [4.2]
EMBEDDER_2 = "intfloat/multilingual-e5-large"    # [4.2] robustness, recall only

READER_MAX_TOKENS = 96                           # [5.1]
# Context window given to vLLM. Readers need room for 20-session Hindi histories (~22k Qwen tokens, see
# DEVIATIONS #10); 32,768 is Qwen3-8B's native context. Judge and translator prompts are short.
MAX_MODEL_LEN = 32768                            # readers; verified per prompt by tokens.py
SHORT_MODEL_LEN = 8192                           # judge, translator
MODEL_LEN = {"qwen3-8b": MAX_MODEL_LEN, "llama3.1-8b": MAX_MODEL_LEN, "judge": SHORT_MODEL_LEN}
