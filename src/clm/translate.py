"""Stage 1 (GPU, fixed translator Qwen3-8B) [design_spec 3.5, 4.3].

1. Translate the 40 English filler sessions into HI and HG (all turns).
2. Build every history (item x storage language).
3. Translate every HI/HG memory unit and query into English (for S2/S3), cached in en_translations.json.
"""
import json

from . import config, haystack, prompts
from .textutil import HG_MARKERS, devanagari_share


def _write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def translate_fillers(gen, log):
    pool_en = haystack.load_jsonl(config.DATA / "haystacks" / "filler_pool_en.jsonl")
    texts = [t["content"] for s in pool_en for t in s["turns"]]
    hi = gen.chat([prompts.to_hindi(x) for x in texts], max_tokens=400)
    hg = gen.chat([prompts.to_hinglish(x) for x in texts], max_tokens=400)
    # Hinglish must be Roman script. Fallback for turns where Devanagari leaked in: romanize the
    # Hindi translation of the same turn (an easier task than translating from English).
    bad = [i for i, x in enumerate(hg) if devanagari_share(x) > 0.1]
    if bad:
        retry = gen.chat([prompts.romanize_hindi(hi[i]) for i in bad], max_tokens=400)
        for i, x in zip(bad, retry):
            hg[i] = x
    # Second failure mode seen in the r2 spot check: the model returns the English text unchanged. Catch long turns
    # with almost no Hindi function words and romanize the Hindi version instead.
    english_leak = [i for i, x in enumerate(hg) if i not in bad and len(x.split()) >= 12
                    and sum(w in HG_MARKERS for w in x.lower().split()) / len(x.split()) < 0.05]
    if english_leak:
        retry = gen.chat([prompts.romanize_hindi(hi[i]) for i in english_leak], max_tokens=400)
        for i, x in zip(english_leak, retry):
            hg[i] = x
    log["hinglish_english_leak_fixed"] = len(english_leak)
    still = [i for i, x in enumerate(hg) if devanagari_share(x) > 0.1]
    log["filler_turns"] = len(texts)
    log["hinglish_fewshot_failures"] = len(bad)
    log["hinglish_still_devanagari"] = len(still)
    log["hindi_low_devanagari"] = sum(devanagari_share(x) < 0.5 for x in hi)
    print("filler translation:", log)
    # Fail loudly rather than silently building half-Devanagari "Hinglish" histories [design_spec 3.5].
    # (Skipped for the mock backend, whose "translations" are English copies by design.)
    if gen.backend != "mock" and (len(still) > 0.05 * len(texts) or log["hindi_low_devanagari"] > 0.05 * len(texts)):
        raise RuntimeError(f"Filler translation quality check failed: {log}. Hinglish/Hindi fillers not saved.")
    for lang, outs in (("hi", hi), ("hg", hg)):
        it = iter(outs)
        rows = [{**s, "turns": [{"role": t["role"], "content": next(it)} for t in s["turns"]]} for s in pool_en]
        _write_jsonl(haystack.filler_path(lang), rows)


def run(items_path, backend=None):
    from .llm import Generator
    gen = None

    def translator():   # loaded only if something needs translating (ablation blocks reuse the main cache)
        nonlocal gen
        if gen is None:
            gen = Generator(config.TRANSLATOR, backend=backend, max_model_len=config.SHORT_MODEL_LEN)
        return gen

    log = {}
    if not (haystack.filler_path("hi").exists() and haystack.filler_path("hg").exists()):
        translate_fillers(translator(), log)
    items = haystack.load_items(items_path)
    hist = haystack.build_all(items, haystack.load_fillers())
    _write_jsonl(config.RESULTS / "histories.jsonl", hist)

    cache_path = config.TRANSLATION_CACHE
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    todo = set()
    for h in hist:
        if h["lang"] != "en":
            todo.update(text for _, text in haystack.units(h))
    for it in items:
        for lang in ("hi", "hg"):
            todo.update(it["text"][lang][q] for q in config.QUERY_VARIANTS)
    todo = sorted(x for x in todo if x not in cache)
    if todo:
        for src, out in zip(todo, translator().chat([prompts.to_english(x) for x in todo], max_tokens=300)):
            cache[src] = out
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
    log["en_translations"] = len(cache)
    log["newly_translated"] = len(todo)
    log["block"], log["n_sessions"] = config.BLOCK, config.N_SESSIONS
    (config.RESULTS / "log_translate.json").write_text(json.dumps(log, indent=2))
    print("translate stage:", log)
