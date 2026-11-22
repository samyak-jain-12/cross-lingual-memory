"""Stage 5 (CPU): score every generation and write the analysis tables [design_spec 1, 6].

Outputs in results/<run>/:
  scored.csv                    one row per (model, item, store, query, qv, setup)
  table_accuracy_3x3.csv        accuracy per model x setup x store x query
  table_gap.csv                 H1: monolingual vs cross-lingual gap (paired by item, bootstrap CI)
  table_mirror.csv              H2: mirrored directions, exact McNemar
  table_recall.csv              recall@k per retriever x strategy x store x query
  table_stages.csv              where failures happen: retrieval miss / reading error / oracle error
  table_noise_floor.csv         paraphrase disagreement on monolingual cells
  table_abstention.csv          hallucination rate on unanswerable controls
  table_response_language.csv   answer language by query language
  judge_validation_sample.csv   200 stratified responses for human labelling
  summary.md                    human-readable digest
"""
import csv
import json
import random
from collections import defaultdict

from . import config, haystack
from .textutil import any_match, is_abstention, response_language, slot_match

CROSS = [(s, q) for s in config.LANGS for q in config.LANGS if s != q]
DIAG = [(l, l) for l in config.LANGS]


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value from discordant counts b, c."""
    from math import comb
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def score_rows(items):
    judg = {(j["id"], j["model"]): j["judge"] for j in haystack.load_jsonl(config.RESULTS / "judgments.jsonl")} \
        if (config.RESULTS / "judgments.jsonl").exists() else {}
    ret = {(r["item_id"], r["store"], r["query"], r["qv"], r["strategy"]): r
           for r in haystack.load_jsonl(config.RESULTS / "retrieval.jsonl") if r["retriever"] == "bge-m3"}
    rows = []
    for p in sorted(config.RESULTS.glob("generations_*.jsonl")):
        for g in haystack.load_jsonl(p):
            iid, s, q, qv, setup = g["id"].split("|")
            it = items[iid]
            ans = it.get("is_answerable", True)
            resp = g["response"]
            j = judg.get((g["id"], g["model"]))
            if ans:
                slots = it["gold"]["slots"]
                correct = (j == "CORRECT") if j else slot_match(resp, slots)
                sm = slot_match(resp, slots)
            else:
                correct = (j == "NO_ANSWER") if j else is_abstention(resp)
                sm = None
            gold_rank = ret[(iid, s, q, qv, setup.split("-")[1])]["gold_rank"] if setup.startswith("RM") and ans else None
            rows.append({
                "model": g["model"], "item_id": iid, "memory_type": it["memory_type"], "answerable": ans,
                "store": s, "query": q, "qv": qv, "setup": setup, "judge": j or "", "correct": int(bool(correct)),
                "slot_match": "" if sm is None else int(sm),
                "distractor_capture": int(any_match(resp, it.get("distractor", {}).get("value_aliases"))) if ans else "",
                "near_miss_capture": int(any_match(resp, it.get("near_miss_aliases"))) if ans else "",
                "abstained": int(is_abstention(resp)), "resp_lang": response_language(resp),
                "gold_rank": gold_rank if gold_rank is not None else "", "response": resp})
    return rows


def write_csv(name, rows):
    if not rows:
        return
    # utf-8-sig adds the BOM that Excel needs to display Hindi correctly (plain utf-8 shows garbage on Mac Excel).
    with open(config.RESULTS / name, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def item_level(rows, model, setup, cells):
    """Per item: mean correctness over the given cells (both query variants)."""
    acc = defaultdict(list)
    for r in rows:
        if r["model"] == model and r["setup"] == setup and r["answerable"] and (r["store"], r["query"]) in cells:
            acc[r["item_id"]].append(r["correct"])
    return {k: mean(v) for k, v in acc.items()}


def bootstrap_ci(diffs, n=10000, seed=0):
    rng = random.Random(seed)
    if not diffs:
        return float("nan"), float("nan")
    means = sorted(mean(rng.choices(diffs, k=len(diffs))) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


def run(items_path):
    items = {i["item_id"]: i for i in haystack.load_items(items_path)}
    rows = score_rows(items)
    write_csv("scored.csv", rows)
    models = sorted({r["model"] for r in rows})
    setups = [s for s in config.SETUPS if any(r["setup"] == s for r in rows)]
    ans = [r for r in rows if r["answerable"]]
    md = [f"# Results summary ({config.RESULTS.name})", "",
          f"Generations scored: {len(rows)} | answerable: {len(ans)} | models: {', '.join(models)}", ""]

    # --- 3x3 accuracy ---
    t3 = []
    for m in models:
        for st in setups:
            for s in config.LANGS:
                for q in config.LANGS:
                    xs = [r["correct"] for r in ans if (r["model"], r["setup"], r["store"], r["query"]) == (m, st, s, q)]
                    t3.append({"model": m, "setup": st, "store": s, "query": q, "n": len(xs), "accuracy": round(mean(xs), 4)})
    write_csv("table_accuracy_3x3.csv", t3)
    md += ["## Accuracy (rows = storage language, columns = query language)", ""]
    for m in models:
        for st in setups:
            md += [f"**{m} / {st}**", "", "| store \\ query | EN | HI | HG |", "|---|---|---|---|"]
            for s in config.LANGS:
                cells = [next(x for x in t3 if (x["model"], x["setup"], x["store"], x["query"]) == (m, st, s, q))["accuracy"]
                         for q in config.LANGS]
                md.append(f"| {s.upper()} | " + " | ".join(f"{c:.0%}" for c in cells) + " |")
            md.append("")

    # --- H1 gap (paired by item) ---
    gap = []
    for m in models:
        for st in setups:
            d, c = item_level(ans, m, st, DIAG), item_level(ans, m, st, CROSS)
            diffs = [d[k] - c[k] for k in d if k in c]
            lo, hi = bootstrap_ci(diffs)
            gap.append({"model": m, "setup": st, "n_items": len(diffs), "mono_acc": round(mean(d.values()), 4),
                        "cross_acc": round(mean(c.values()), 4), "gap": round(mean(diffs), 4),
                        "ci95_low": round(lo, 4), "ci95_high": round(hi, 4)})
    write_csv("table_gap.csv", gap)
    md += ["## H1: monolingual minus cross-lingual accuracy (item-paired, 95% bootstrap CI)", "",
           "| model | setup | mono | cross | gap | 95% CI |", "|---|---|---|---|---|---|"]
    md += [f"| {g['model']} | {g['setup']} | {g['mono_acc']:.0%} | {g['cross_acc']:.0%} | {g['gap']*100:+.1f}pp | "
           f"[{g['ci95_low']*100:+.1f}, {g['ci95_high']*100:+.1f}] |" for g in gap] + [""]

    # --- H2 mirrored directions ---
    mir = []
    key = {(r["model"], r["setup"], r["item_id"], r["store"], r["query"], r["qv"]): r["correct"] for r in ans}
    for m in models:
        for st in setups:
            for a, b in (("hi", "en"), ("hg", "en"), ("hg", "hi")):
                # Unit = item: the two wordings of a question are not independent, so average them per item
                # and count items where one direction scores higher (exact sign / McNemar-type test).
                a_better = b_better = n = 0
                diffs = []
                for iid in items:
                    xs = [key.get((m, st, iid, a, b, qv)) for qv in config.QUERY_VARIANTS]
                    ys = [key.get((m, st, iid, b, a, qv)) for qv in config.QUERY_VARIANTS]
                    if None in xs or None in ys:
                        continue
                    n += 1
                    d = mean(xs) - mean(ys)
                    diffs.append(d)
                    a_better += d > 0
                    b_better += d < 0
                lo, hi = bootstrap_ci(diffs)
                mir.append({"model": m, "setup": st, "direction_A": f"{a}->{b}", "direction_B": f"{b}->{a}",
                            "items": n, "A_better_items": a_better, "B_better_items": b_better,
                            "diff_pp": round(100 * mean(diffs), 1) if diffs else "",
                            "ci95_low_pp": round(100 * lo, 1), "ci95_high_pp": round(100 * hi, 1),
                            "p_exact": round(mcnemar_exact(a_better, b_better), 4)})
    # Holm correction across ALL mirror tests (models x setups x pairs): the honest family size.
    order = sorted(range(len(mir)), key=lambda i: mir[i]["p_exact"])
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(mir) - rank) * mir[i]["p_exact"]))
        mir[i]["p_holm_all"] = round(running, 4)
    write_csv("table_mirror.csv", mir)
    md += [f"## H2: mirrored directions (item-level exact test; Holm over all {len(mir)} tests)", "",
           "| model | setup | A vs B | items A better / B better | diff (pp) [95% CI] | p | p (Holm) |",
           "|---|---|---|---|---|---|---|"]
    md += [f"| {r['model']} | {r['setup']} | {r['direction_A']} vs {r['direction_B']} | {r['A_better_items']} / "
           f"{r['B_better_items']} | {r['diff_pp']} [{r['ci95_low_pp']}, {r['ci95_high_pp']}] | {r['p_exact']} | "
           f"{r['p_holm_all']} |" for r in sorted(mir, key=lambda r: r["p_exact"])[:6]]
    md += ["(6 smallest p-values shown; full table in table_mirror.csv)", ""]

    # --- Recall@k ---
    rec = []
    rr = [r for r in haystack.load_jsonl(config.RESULTS / "retrieval.jsonl") if r["gold_rank"]]
    for name in sorted({r["retriever"] for r in rr}):
        for strat in ("S1", "S2", "S3"):
            for s in config.LANGS:
                for q in config.LANGS:
                    ranks = [r["gold_rank"] for r in rr if (r["retriever"], r["strategy"], r["store"], r["query"]) == (name, strat, s, q)]
                    rec.append({"retriever": name, "strategy": strat, "store": s, "query": q, "n": len(ranks),
                                **{f"R@{k}": round(mean(int(x <= k) for x in ranks), 4) for k in config.RECALL_KS}})
    write_csv("table_recall.csv", rec)
    md += ["## Recall@5 (bge-m3), mono vs cross", "", "| strategy | mono R@5 | cross R@5 |", "|---|---|---|"]
    for strat in ("S1", "S2", "S3"):
        sub = [x for x in rec if x["retriever"] == "bge-m3" and x["strategy"] == strat]
        md.append(f"| {strat} | {mean(x['R@5'] for x in sub if x['store'] == x['query']):.0%} | "
                  f"{mean(x['R@5'] for x in sub if x['store'] != x['query']):.0%} |")
    md.append("")

    # --- Stage decomposition (RM vs OR) ---
    stg = []
    for m in models:
        for strat in ("S1", "S2", "S3"):
            for s in config.LANGS:
                for q in config.LANGS:
                    rm = [r for r in ans if (r["model"], r["setup"], r["store"], r["query"]) == (m, f"RM-{strat}", s, q)]
                    orc = [r for r in ans if (r["model"], r["setup"], r["store"], r["query"]) == (m, f"OR-{strat}", s, q)]
                    if not rm:
                        continue
                    hit = [r for r in rm if r["gold_rank"] != "" and int(r["gold_rank"]) <= config.TOP_K]
                    stg.append({"model": m, "strategy": strat, "store": s, "query": q, "n": len(rm),
                                "retrieval_miss": round(1 - len(hit) / len(rm), 4),
                                "reading_error_given_hit": round(1 - mean(r["correct"] for r in hit), 4) if hit else "",
                                "oracle_error": round(1 - mean(r["correct"] for r in orc), 4) if orc else "",
                                "end_to_end_error": round(1 - mean(r["correct"] for r in rm), 4)})
    write_csv("table_stages.csv", stg)

    # --- Noise floor (paraphrase disagreement on monolingual cells) ---
    nf = []
    for m in models:
        for st in setups:
            dis = [int(key[(m, st, iid, l, l, "q1")] != key[(m, st, iid, l, l, "q2")])
                   for iid in items for l in config.LANGS
                   if (m, st, iid, l, l, "q1") in key and (m, st, iid, l, l, "q2") in key]
            nf.append({"model": m, "setup": st, "pairs": len(dis), "paraphrase_disagreement": round(mean(dis), 4)})
    write_csv("table_noise_floor.csv", nf)

    # --- Abstention controls ---
    ab = [r for r in rows if not r["answerable"]]
    abt = []
    for m in models:
        for st in setups:
            for s, q in DIAG + CROSS:
                xs = [1 - r["correct"] for r in ab if (r["model"], r["setup"], r["store"], r["query"]) == (m, st, s, q)]
                if xs:
                    abt.append({"model": m, "setup": st, "store": s, "query": q, "n": len(xs), "hallucination_rate": round(mean(xs), 4)})
    write_csv("table_abstention.csv", abt)

    # --- Response language ---
    rl = []
    for m in models:
        for q in config.LANGS:
            sub = [r for r in rows if r["model"] == m and r["query"] == q]
            rl.append({"model": m, "query_lang": q, "n": len(sub),
                       **{f"answered_{l}": round(mean(int(r["resp_lang"] == l) for r in sub), 4) for l in ("en", "hi", "hg", "other")}})
    write_csv("table_response_language.csv", rl)

    # --- Judge sanity + human-validation sample ---
    judged = [r for r in ans if r["judge"]]
    if judged:
        agree = mean(int((r["judge"] == "CORRECT") == bool(r["slot_match"])) for r in judged)
        md += [f"Judge vs slot-match agreement (answerable): {agree:.1%} over {len(judged)} responses "
               "(disagreements are what the human validation must resolve).", ""]
    rng = random.Random(7)
    strata = defaultdict(list)
    for r in rows:
        strata[(r["model"], r["store"], r["query"])].append(r)
    sample = []
    for k in sorted(strata):
        sample += rng.sample(strata[k], min(len(strata[k]), -(-200 // len(strata))))
    write_csv("judge_validation_sample.csv",
              [{"model": r["model"], "item_id": r["item_id"], "store": r["store"], "query": r["query"], "qv": r["qv"],
                "setup": r["setup"], "question": items[r["item_id"]]["text"][r["query"]][r["qv"]],
                "gold": items[r["item_id"]].get("gold", {}).get("answer_en", ""), "response": r["response"],
                "judge": r["judge"], "human_label (CORRECT/INCORRECT/NO_ANSWER)": ""} for r in sample[:200]])
    (config.RESULTS / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md[:60]))
