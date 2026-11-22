"""Normalization and deterministic checks used in scoring [design_spec 6.1]."""
import re
import unicodedata

DEV_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
NUKTA = "़"
DEVANAGARI = re.compile(r"[ऀ-ॿ]")
LATIN = re.compile(r"[A-Za-z]")

# Common Hindi function words in Roman script: their presence marks Hinglish rather than English.
HG_MARKERS = {"hai", "hain", "tha", "thi", "nahi", "nahin", "kya", "mera", "meri", "mere", "mujhe", "aap", "aapka",
              "aapki", "ka", "ki", "ke", "ko", "se", "mein", "aur", "ya", "toh", "hoon", "kar", "karti", "karta",
              "liya", "gaya", "gayi", "pe", "par", "wala", "wali", "kab", "kahan", "kitna", "kitne", "pata"}

ABSTAIN = re.compile(
    r"(don't know|do not know|not sure|no information|not (been )?mentioned|didn't (mention|tell|say)|"
    r"haven't (mentioned|told)|not in (our|the|my) (past )?conversations?|no record|cannot (find|determine)|"
    r"can't (find|determine)|pata nahi|nahi pata|nahin pata|jaankari nahi|maloom nahi|"
    r"नहीं पता|पता नहीं|जानकारी नहीं|उल्लेख नहीं|मालूम नहीं|नहीं बताया)", re.I)


def norm(s):
    s = unicodedata.normalize("NFC", s or "").translate(DEV_DIGITS).replace(NUKTA, "")
    s = s.replace("’", "'").replace("–", "-").replace("—", "-")
    return s.casefold()


def contains_exact(text, alias):
    """Word-bounded match for Latin aliases, substring match for Devanagari (after normalization).

    Used to build data (banned fillers, QA), where matching must not change once items are frozen.
    """
    t, a = norm(text), norm(alias)
    if not a:
        return False
    if re.search(r"[a-z0-9]", a):
        return re.search(rf"(?<![a-z0-9]){re.escape(a)}(?![a-z0-9])", t) is not None
    return a in t


# ---------------- lenient matching for scoring (ENDSEM_PLAN §3 change 4) ----------------
# The pilot's slot checker missed 237 answers the judge accepted (188 in Hindi): spelling variants (नाइके/नाइकी,
# लुना/लूना), gender/number endings (पीला/पीली/पीले), Hinglish month names ("10 janvar") and number words before
# units ("do hafta"). canon() maps all of these onto one form; contains() tries the exact match first.
_DEV_FOLD = str.maketrans({"ी": "ि", "ू": "ु", "ई": "इ", "ऊ": "उ", "ँ": "ं", "ॉ": "ा", "ऑ": "आ", "ॅ": "े", "ऍ": "ए"})
_DEV_FINAL = ("ं", "ि", "े", "ो")               # word-final endings stripped; "ा" kept: नाइका (Nykaa) must not match नाइकी (Nike)
_TOKEN = re.compile(r"[ऀ-ॿ]+|[a-z0-9]+(?:[:.%][0-9]+%?|%)?")
_MONTHS_HG = {
    "january": ("janvari", "janvary", "janvar", "janwari", "jan"), "february": ("farvari", "farwari", "faravari", "feb"),
    "march": ("maarch",), "april": ("aprail", "apral", "apr"), "may": ("mai",), "june": ("joon", "jun"),
    "july": ("julai", "jul"), "august": ("agast", "aug"), "september": ("sitambar", "sitmbar", "sep", "sept"),
    "october": ("aktubar", "aktoobar", "oct"), "november": ("navambar", "nov"), "december": ("disambar", "dec")}
_MONTH_OF = {v: k for k, vs in _MONTHS_HG.items() for v in vs}
_UNIT_HG = {"hafta": "hafte", "hafton": "hafte", "hafe": "hafte", "hafee": "hafte", "haftay": "hafte", "ghanta": "ghante", "ghanton": "ghante", "mahina": "mahine",
            "mahino": "mahine", "mahinon": "mahine", "minat": "minute", "mint": "minute", "minutes": "minute"}
_UNITS = {"hafte", "ghante", "mahine", "din", "saal", "minute", "weeks", "week", "hours", "hour", "months", "month",
          "days", "day", "years", "year", "skeins", "bikes", "shirts", "bass", "comedians",
          "हफ्त", "घंट", "महिन", "दिन", "साल", "मिनट"}
_NUM_WORDS = {w: str(i) for i, ws in enumerate((
    (), ("ek", "one", "एक"), ("do", "two", "दो"), ("teen", "three", "तिन"), ("char", "chaar", "four", "चार"),
    ("paanch", "panch", "five", "पांच"), ("chhe", "chhah", "che", "six", "छह", "छः", "छ"), ("saat", "seven", "सात"),
    ("aath", "eight", "आठ"), ("nau", "nine", "नौ"), ("das", "ten", "दस"), ("gyarah", "eleven", "ग्यारह"),
    ("barah", "baarah", "twelve", "बारह"))) for w in ws}


def _dev_stem(tok):
    tok = tok.translate(_DEV_FOLD)
    for _ in range(2):                           # e.g. जूतों -> जुतो -> जुत
        if len(tok) > 2 and tok.endswith(_DEV_FINAL):
            tok = tok[:-1]
    return tok


def canon(s):
    """Space-joined canonical tokens: Devanagari folded and de-inflected, Hinglish months and units unified,
    number words before a unit turned into digits."""
    toks = _TOKEN.findall(norm(s))
    out = []
    for t in toks:
        if re.match(r"[ऀ-ॿ]", t):
            out.append(_dev_stem(t))
        else:
            t = _MONTH_OF.get(t, t)
            out.append(_UNIT_HG.get(t, t))
    for i in range(len(out) - 1):
        if out[i + 1] in _UNITS and out[i] in _NUM_WORDS:
            out[i] = _NUM_WORDS[out[i]]
    return " ".join(out)


def _drop_aa(tok):
    return tok[:-1] if len(tok) > 2 and tok.endswith("ा") else tok


def contains(text, alias):
    """Scoring match: exact (contains_exact) or, failing that, a token-window match of canonical forms.

    A final "ा" is also ignored, but only for alias words that are NOT the last word: agreement changes
    the modifier before a noun (पीला/पीली ड्रेस), while names usually stand alone or come last (नाइका ≠ नाइकी).
    """
    if contains_exact(text, alias):
        return True
    a, t = canon(alias).split(), canon(text).split()
    if not a:
        return False
    for i in range(len(t) - len(a) + 1):
        if all(x == y or (k < len(a) - 1 and _drop_aa(x) == _drop_aa(y))
               for k, (x, y) in enumerate(zip(a, t[i:i + len(a)]))):
            return True
    return False


def slot_match(response, slots):
    """All gold slots present (any alias, any script)."""
    return bool(slots) and all(any(contains(response, a) for a in s["aliases"]) for s in slots)


def any_match(response, aliases):
    return any(contains(response, a) for a in aliases or [])


def is_abstention(response):
    return bool(ABSTAIN.search(response or ""))


def response_language(text):
    """'hi' (Devanagari), 'hg' (romanized Hindi), 'en', or 'other'."""
    dev, lat = len(DEVANAGARI.findall(text or "")), len(LATIN.findall(text or ""))
    if dev + lat == 0:
        return "other"
    if dev / (dev + lat) > 0.3:
        return "hi"
    words = re.findall(r"[a-z]+", (text or "").lower())
    hg = sum(w in HG_MARKERS for w in words)
    return "hg" if words and (hg >= 2 or hg / len(words) > 0.15) else "en"


def devanagari_share(text):
    dev, lat = len(DEVANAGARI.findall(text or "")), len(LATIN.findall(text or ""))
    return dev / (dev + lat) if dev + lat else 0.0
