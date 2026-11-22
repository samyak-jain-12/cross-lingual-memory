"""Stage 2 (GPU or CPU): rank memory units for every query [design_spec 4.1-4.2].

Strategies (what is indexed / what the query is):
  S1 original : original units            / original query
  S2 pivot    : English translations       / English translation of the query
  S3 dual     : original + English (merged by unit, max score) / original query
Retrievers: bge-m3 (feeds the readers), multilingual-e5 and BM25 (recall only).
"""
import json
import math
import re
from collections import Counter

import numpy as np

from . import config, haystack

TOKEN = re.compile(r"[^\s.,!?;:'\"()\[\]\-–—/।]+")


class DenseEmbedder:
    def __init__(self, model_id, backend="st"):
        self.model_id, self.backend = model_id, backend
        self.e5 = "e5" in model_id
        if backend == "st":
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_id, device="cuda" if _has_cuda() else "cpu")
        self.cache = {}

    def _mock(self, text):
        v = np.zeros(512)
        t = text.lower()
        for i in range(len(t) - 2):
            v[hash(t[i:i + 3]) % 512] += 1
        return v

    def embed(self, texts, is_query):
        prefix = ("query: " if is_query else "passage: ") if self.e5 else ""
        need = [t for t in dict.fromkeys(texts) if (prefix + t) not in self.cache]
        if need:
            if self.backend == "st":
                vecs = self.model.encode([prefix + t for t in need], batch_size=32, normalize_embeddings=True,
                                         show_progress_bar=False)
            else:
                vecs = [self._mock(t) for t in need]
                vecs = [v / (np.linalg.norm(v) or 1) for v in vecs]
            for t, v in zip(need, vecs):
                self.cache[prefix + t] = np.asarray(v, dtype=np.float32)
        return np.stack([self.cache[prefix + t] for t in texts])

    def scores(self, query, docs):
        return self.embed(docs, False) @ self.embed([query], True)[0]


class BM25:
    k1, b = 1.5, 0.75

    def scores(self, query, docs):
        toks = [TOKEN.findall(d.lower()) for d in docs]
        avg = sum(map(len, toks)) / max(1, len(toks))
        df = Counter(w for t in toks for w in set(t))
        n = len(docs)
        out = []
        for t in toks:
            tf = Counter(t)
            s = 0.0
            for w in TOKEN.findall(query.lower()):
                if w in tf:
                    idf = math.log(1 + (n - df[w] + 0.5) / (df[w] + 0.5))
                    s += idf * tf[w] * (self.k1 + 1) / (tf[w] + self.k1 * (1 - self.b + self.b * len(t) / avg))
            out.append(s)
        return np.array(out)


def _has_cuda():
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def rank(retriever, query, units, strategy, en):
    """Return unit ids ranked best-first."""
    ids = [u for u, _ in units]
    if strategy == "S1":
        sc = retriever.scores(query, [x for _, x in units])
    elif strategy == "S2":
        sc = retriever.scores(en.get(query, query), [en.get(x, x) for _, x in units])
    else:  # S3 dual index: score both representations, keep the max per unit
        a = retriever.scores(query, [x for _, x in units])
        b = retriever.scores(query, [en.get(x, x) for _, x in units])
        sc = np.maximum(a, b)
    order = np.argsort(-np.asarray(sc), kind="stable")
    return [ids[i] for i in order]


def run(items_path, backend=None):
    backend = backend or ("mock" if __import__("os").environ.get("CLM_BACKEND") == "mock" else "st")
    items = haystack.load_items(items_path)
    hist = {(h["item_id"], h["lang"]): h for h in haystack.load_jsonl(config.RESULTS / "histories.jsonl")}
    en = json.loads(config.TRANSLATION_CACHE.read_text(encoding="utf-8"))
    retrievers = {"bge-m3": DenseEmbedder(config.EMBEDDER, backend),
                  "me5": DenseEmbedder(config.EMBEDDER_2, backend),
                  "bm25": BM25()}
    rows = []
    for it in items:
        for s in config.STORE_LANGS:
            h = hist[(it["item_id"], s)]
            units = haystack.units(h)
            for q in config.LANGS:
                for qv in config.QUERY_VARIANTS:
                    query = it["text"][q][qv]
                    for strat in ("S1", "S2", "S3"):
                        for name, r in retrievers.items():
                            ranked = rank(r, query, units, strat, en)
                            gold = h["gold_unit"] if it.get("is_answerable", True) else None
                            rows.append({"item_id": it["item_id"], "store": s, "query": q, "qv": qv,
                                         "strategy": strat, "retriever": name, "ranked": ranked[:10],
                                         "gold_rank": ranked.index(gold) + 1 if gold else None,
                                         "distractor_rank": (ranked.index(h["distractor_unit"]) + 1
                                                             if h["distractor_unit"] else None)})
    with open(config.RESULTS / "retrieval.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"retrieval stage: {len(rows)} rankings")
