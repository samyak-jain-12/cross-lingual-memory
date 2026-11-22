"""Builds the independent-model verification prompts. Shared by src/make_verify.py (local) and the Kaggle
notebook (which embeds this file verbatim), so both produce byte-identical jsonl files.
"""
import json

LANG_NAME = {"hi": "Hindi written in Devanagari script",
             "hg": "Hinglish (Hindi written in Latin script, mixed with English words, as Indians text)"}
AUDIT_FIELDS = ["memory_turn", "followup_turn", "distractor_sentence", "q1", "q2", "q3"]
KEY_COLS = ["model", "item_id", "store", "query", "qv", "setup"]


def judge_rows(keys, scored, items, prompts):
    """keys: list of [model, item_id, store, query, qv, setup]; scored: DataFrame of scored.csv."""
    idx = scored.set_index(KEY_COLS)
    out = []
    for k in keys:
        r = idx.loc[tuple(k)]
        it = items[k[1]]
        query = it["text"][k[3]][k[4]]
        answerable = bool(r["answerable"])
        if answerable:
            aliases = [a for sl in it["gold"]["slots"] for a in sl["aliases"]]
            msgs = prompts.judge(query, it["gold"]["answer_en"], aliases, r["response"])
        else:
            msgs = prompts.judge_abstention(query, r["response"])
        sm = r["slot_match"]
        out.append(dict(sid=f"J{len(out):03d}", model=k[0], item_id=k[1], store=k[2], query=k[3], qv=k[4], setup=k[5],
                        answerable=answerable, slot_match=None if sm != sm else int(sm), qwen_judge=str(r["judge"]),
                        messages=msgs))
    return out


def audit_prompt(it, lang):
    en, tr = it["text"]["en"], it["text"][lang]
    fields = [f for f in AUDIT_FIELDS if en.get(f) and tr.get(f)]
    pairs = "\n".join(f"[{f}]\n  English: {en[f]}\n  {lang.upper()}: {tr[f]}" for f in fields)
    if it["is_answerable"]:
        key = (f"Key fact that must survive in the translated memory_turn: {it['gold']['answer_en']}\n"
               f"Accepted forms: {'; '.join(a for sl in it['gold']['slots'] for a in sl['aliases'])}\n")
    else:
        key = "This item has only questions (no stored fact); key_fact_present should be \"n/a\".\n"
    user = (
        f"You are auditing a translation for a research dataset. Each field below has an English source and its "
        f"version in {LANG_NAME[lang]}.\n{key}\n{pairs}\n\n"
        "Check:\n"
        "1. meaning_same: every translated field means the same as its English source (no added, dropped or changed facts, "
        "names, numbers or dates).\n"
        "2. key_fact_present: the key fact is stated in the translated memory_turn.\n"
        "3. questions_same: the translated questions ask for the same information as the English ones.\n"
        f"4. natural: it reads like natural {'Hindi' if lang == 'hi' else 'Hinglish'} a native speaker would write.\n"
        "Reply with only this JSON, no other text:\n"
        '{"meaning_same": "yes|no", "key_fact_present": "yes|no|n/a", "questions_same": "yes|no", '
        '"natural": "yes|no", "problems": "<short description, or none>"}'
    )
    return fields, [{"role": "user", "content": user}]


def audit_rows(items):
    out = []
    for iid, it in items.items():
        for lang in ("hi", "hg"):
            fields, msgs = audit_prompt(it, lang)
            out.append(dict(aid=f"{iid}|{lang}", item_id=iid, lang=lang, answerable=it["is_answerable"],
                            fields=fields, messages=msgs))
    return out


def dumps(rows):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
