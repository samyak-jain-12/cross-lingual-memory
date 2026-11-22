"""Build conversation histories [design_spec 3.5].

Every item gets an n-session history per storage language (config.N_SESSIONS: 20 in the main run, 10 for
the Short ablation and the pilot). Filler choice, evidence position and
distractor placement depend only on the item's seed, so the three language versions of a history
differ in language and nothing else. Unanswerable controls reuse their base item's history.
"""
import json
import random

from . import config


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def load_items(path):
    """Items of the current block (config.ITEM_FLAG, set by src/merge_items.py); the main block keeps everything."""
    items = load_jsonl(path)
    return [i for i in items if i.get(config.ITEM_FLAG)] if config.ITEM_FLAG else items


ASCII_TO_DEV = str.maketrans("0123456789", "०१२३४५६७८९")


def to_devanagari_digits(text):
    """Ablation C: write every number in a Hindi history with Devanagari digits (15 -> १५)."""
    return text.translate(ASCII_TO_DEV)


def filler_path(lang):
    """EN pool lives in data/; HI/HG pools come from this run's translate stage, unless frozen copies exist in data/."""
    frozen = config.DATA / "haystacks" / f"filler_pool_{lang}.jsonl"
    return frozen if lang == "en" or frozen.exists() else config.RESULTS / f"filler_pool_{lang}.jsonl"


def load_fillers():
    pools = {}
    for lang in config.LANGS:
        p = filler_path(lang)
        if p.exists():
            pools[lang] = {s["filler_id"]: s for s in load_jsonl(p)}
    return pools


def evidence_slot(base, n):
    """Session slot of the evidence: from the position class (main study) or the fixed pilot slot (old items)."""
    if "evidence_class" in base:
        return config.EVIDENCE_SLOT[base["evidence_class"]](n)
    return base["evidence_position"]


def layout(base, n=None):
    """Deterministic layout shared by all languages: which filler goes in which slot, where the distractor is.

    Fillers are always drawn for MAX_SESSIONS and a shorter history takes the first n-1 of them, so the
    Short history is a subset of the Long one. The distractor's host is drawn from its own seeded stream.
    """
    n = n or config.N_SESSIONS
    rng = random.Random(base["filler_seed"])
    banned = set(base.get("banned_fillers", []))   # fillers mentioning the gold value [3.5]; set by merge_items.py
    pool = [i for i in range(1, config.FILLER_POOL_SIZE + 1) if f"FL{i:02d}" not in banned]
    filler_ids = [f"FL{i:02d}" for i in rng.sample(pool, config.MAX_SESSIONS - 1)][: n - 1]
    ev = evidence_slot(base, n)
    slots, it = {}, iter(filler_ids)
    for k in range(1, n + 1):
        slots[k] = "EVIDENCE" if k == ev else next(it)
    host = None
    if base.get("has_distractor"):
        host = random.Random(f"{base['filler_seed']}-dis-{n}").choice(
            [k for k in slots if slots[k] != "EVIDENCE" and abs(k - ev) >= 2])
    return slots, host


def build(base, lang, fillers, n=None):
    """Return {'sessions': [[turn,...],...], 'gold_unit', 'distractor_unit'}; user turns carry a unit_id."""
    n = n or config.N_SESSIONS
    slots, host = layout(base, n)
    t = base["text"][lang]
    sessions, gold_unit, dis_unit = [], None, None
    for k in range(1, n + 1):
        if slots[k] == "EVIDENCE":
            turns = [{"role": "user", "content": t["memory_turn"]},
                     {"role": "assistant", "content": t["assistant_reply"]},
                     {"role": "user", "content": t["followup_turn"]},
                     {"role": "assistant", "content": t["followup_reply"]}]
        else:
            turns = [dict(x) for x in fillers[lang][slots[k]]["turns"]]
            if k == host:
                turns[0]["content"] = turns[0]["content"].rstrip() + " " + t["distractor_sentence"]
        u = 0
        for turn in turns:
            if turn["role"] == "user":
                u += 1
                turn["unit_id"] = f"s{k}u{u}"
        if slots[k] == "EVIDENCE":
            gold_unit = f"s{k}u1"
        if k == host:
            dis_unit = f"s{k}u1"
        if config.DEV_DIGITS and lang == "hi":
            for turn in turns:
                turn["content"] = to_devanagari_digits(turn["content"])
        sessions.append(turns)
    return {"sessions": sessions, "gold_unit": gold_unit, "distractor_unit": dis_unit,
            "filler_ids": [slots[k] for k in sorted(slots)]}


def build_all(items, fillers, n=None):
    n = n or config.N_SESSIONS
    by_id = {i["item_id"]: i for i in items}
    out = []
    for it in items:
        base = it if it.get("is_answerable", True) else by_id[it["base_item"]]
        for lang in config.STORE_LANGS:
            h = build(base, lang, fillers, n)
            out.append({"item_id": it["item_id"], "lang": lang, "n_sessions": n, **h})
    return out


def units(history):
    """User turns as memory units, in chronological order."""
    return [(t["unit_id"], t["content"]) for s in history["sessions"] for t in s if t["role"] == "user"]
