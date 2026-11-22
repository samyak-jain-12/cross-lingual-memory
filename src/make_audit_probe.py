"""Planted-error test for the Aya translation audit (DEVIATIONS #14).

The real audit (src/make_verify.py) passed 330/330, which only means something if Aya can catch a bad
translation. This builds 48 deliberately broken Hindi/Hinglish versions of answerable items, in the exact audit
prompt format (verify_build.audit_prompt), and a small Kaggle notebook that runs Aya on them.

Four corruption types, 12 items each (6 hi, 6 hg), 48 distinct items, seed 20261121:
  fact_swap      the key fact in the translated memory_turn is replaced by another item's value of the same kind
  fact_drop      the key fact is deleted from the translated memory_turn
  question_swap  the translated q1 is replaced by another item's q1 (same language)
  memory_swap    the translated memory_turn is replaced by another item's memory_turn (same language)
Detection = Aya answers "no" to the check that the corruption breaks (expected_fail), or to any core check.

Run from the project root:  python3 src/make_audit_probe.py
Writes data/verify/audit_probe.jsonl and kaggle/verify_aya_probe.ipynb (no Kaggle input needed).
"""
import copy
import hashlib
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from make_kaggle_notebook import code, md, writefile  # noqa: E402
import verify_build as vb  # noqa: E402

MODEL = "CohereLabs/aya-expanse-8b"
VLLM_VERSION = "0.30.0"
SEED = 20261121
TYPES = ["fact_swap", "fact_drop", "question_swap", "memory_swap"]
EXPECTED = {"fact_swap": ["meaning_same", "key_fact_present"], "fact_drop": ["meaning_same", "key_fact_present"],
            "question_swap": ["meaning_same", "questions_same"], "memory_swap": ["meaning_same", "key_fact_present"]}
DEV = re.compile(r"[ऀ-ॿ]")


def aliases(it):
    return [a for sl in it["gold"]["slots"] for a in sl["aliases"]]


def build():
    rng = random.Random(SEED)
    items = [json.loads(l) for l in open(ROOT / "data/items/items_main.jsonl", encoding="utf-8")]
    ans = [it for it in items if it["is_answerable"]]
    pool = ans[:]
    rng.shuffle(pool)
    rows = []
    for t in TYPES:
        for k in range(12):
            lang = "hi" if k < 6 else "hg"
            it = pool.pop()
            bad = copy.deepcopy(it)
            tr = bad["text"][lang]
            if t in ("fact_swap", "fact_drop"):
                # every occurrence of every gold alias (all slots, longest first) is removed or swapped,
                # so no form of the key fact survives in the translated memory_turn
                own = {x.lower() for x in aliases(it)}
                done = []
                for sl in it["gold"]["slots"]:
                    for a in sorted(sl["aliases"], key=len, reverse=True):
                        if a.lower() not in tr["memory_turn"].lower():
                            continue
                        if t == "fact_drop":
                            new = ""
                        else:
                            same = lambda s: bool(DEV.search(s)) == bool(DEV.search(a))  # noqa: E731
                            cands = [x for o in ans if o is not it for s2 in o["gold"]["slots"]
                                     if s2["name"] == sl["name"] for x in s2["aliases"]
                                     if same(x) and x.lower() not in own]
                            cands = cands or [x for o in ans if o is not it for x in aliases(o)
                                              if same(x) and x.lower() not in own]
                            new = rng.choice(cands)
                        tr["memory_turn"] = re.sub(re.escape(a), new.replace("\\", r"\\"), tr["memory_turn"],
                                                   flags=re.I)
                        done.append(f"'{a}' -> '{new}'" if new else f"removed '{a}'")
                tr["memory_turn"] = re.sub(r"\s{2,}", " ", tr["memory_turn"]).strip()
                assert not any(x in tr["memory_turn"].lower() for x in own), (t, it["item_id"])
                change = "; ".join(done)
            else:
                field = "q1" if t == "question_swap" else "memory_turn"
                donor = rng.choice([o for o in ans if o is not it and o["text"][lang][field] != tr[field]])
                tr[field] = donor["text"][lang][field]
                change = f"{field} taken from {donor['item_id']}"
            assert tr != it["text"][lang], (t, it["item_id"])
            fields, msgs = vb.audit_prompt(bad, lang)
            rows.append(dict(aid=f"P{len(rows):02d}|{it['item_id']}|{lang}", item_id=it["item_id"], lang=lang,
                             answerable=True, corruption=t, expected_fail=EXPECTED[t], change=change,
                             fields=fields, messages=msgs))
    return rows


RUNNER = f'''"""Run Aya Expanse 8B on the planted-error audit probe (greedy, fp16, 2xT4)."""
import json, time
from vllm import LLM, SamplingParams
llm = LLM(model="{MODEL}", dtype="half", tensor_parallel_size=2, max_model_len=4096,
          gpu_memory_utilization=0.88, seed=0)
rows = [json.loads(l) for l in open("/kaggle/working/verify/audit_probe.jsonl", encoding="utf-8")]
t = time.time()
res = llm.chat([r["messages"] for r in rows], SamplingParams(temperature=0.0, max_tokens=300), use_tqdm=True)
with open("/kaggle/working/verify/aya_probe.jsonl", "w", encoding="utf-8") as f:
    for r, o in zip(rows, res):
        r = {{k: v for k, v in r.items() if k != "messages"}}
        r["aya_raw"] = o.outputs[0].text.strip()
        f.write(json.dumps(r, ensure_ascii=False) + "\\n")
print(f"aya_probe: {{len(rows)}} rows in {{time.time() - t:.0f}}s")
'''


def notebook(probe_text, sha):
    return {"cells": [
        md(f"""
# Cross-Lingual Memory: planted-error test of the Aya translation audit

48 deliberately broken Hindi/Hinglish items in the exact audit prompt format. If **{MODEL}** catches most of them,
the 330/330 pass of the real audit is informative. Settings: **GPU T4 x2**, **Internet on**, secret **`HF_TOKEN`**.
No input needed. Run with **Save Version → Save & Run All**.
"""),
        code(f"""
!nvidia-smi --query-gpu=name,memory.total --format=csv
!pip install -q vllm=={VLLM_VERSION} 2>&1 | tail -2
!pip uninstall -y -q torchaudio
import os, json, hashlib, subprocess, shutil
r = subprocess.run(["python", "-c", "import torch, vllm; print('GPUs', torch.cuda.device_count(), 'vllm', vllm.__version__); assert torch.cuda.device_count() == 2"],
                   capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-1500:])
if r.returncode != 0:
    raise RuntimeError("STOP: environment check failed")
"""),
        code(f"""
from kaggle_secrets import UserSecretsClient
os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")
os.environ["HUGGING_FACE_HUB_TOKEN"] = os.environ["HF_TOKEN"]
print("HF token loaded:", bool(os.environ["HF_TOKEN"]))
from huggingface_hub import hf_hub_download
hf_hub_download("{MODEL}", "config.json", token=os.environ["HF_TOKEN"]); print("Aya access: OK")
"""),
        code("!mkdir -p /kaggle/working/verify"),
        writefile("/kaggle/working/verify/audit_probe.jsonl", probe_text),
        writefile("/kaggle/working/verify/run_aya_probe.py", RUNNER),
        code(f"""
text = open("/kaggle/working/verify/audit_probe.jsonl", encoding="utf-8").read()
ok = hashlib.sha256(text.encode("utf-8")).hexdigest() == "{sha}"
print("audit_probe", text.count("\\n"), "rows, sha256 match:", ok)
if not ok:
    raise RuntimeError("STOP: probe file differs from the local one")
r = subprocess.run(["python", "/kaggle/working/verify/run_aya_probe.py"], capture_output=True, text=True)
print(r.stdout[-2000:])
if r.returncode != 0:
    print(r.stderr[-5000:]); raise RuntimeError("STOP: Aya run failed (see above)")
rows = [json.loads(l) for l in open("/kaggle/working/verify/aya_probe.jsonl", encoding="utf-8")]
for x in rows[:4]:
    print(x["corruption"], "|", x["aya_raw"][:200].replace("\\n", " "))
shutil.make_archive("/kaggle/working/verify_aya_probe", "zip", "/kaggle/working/verify")
print("Download zip: /kaggle/working/verify_aya_probe.zip (Output tab)")
"""),
    ], "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                    "language_info": {"name": "python"},
                    "kaggle": {"accelerator": "nvidiaTeslaT4", "isInternetEnabled": True}},
        "nbformat": 4, "nbformat_minor": 4}


def main():
    rows = build()
    text = vb.dumps(rows)
    out = ROOT / "data" / "verify" / "audit_probe.jsonl"
    out.write_text(text, encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    p = ROOT / "kaggle" / "verify_aya_probe.ipynb"
    p.write_text(json.dumps(notebook(text, sha), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"probe: {len(rows)} rows ({', '.join(f'{t} {sum(r['corruption'] == t for r in rows)}' for t in TYPES)}); "
          f"sha256 {sha[:12]}")
    print(f"wrote {out.relative_to(ROOT)} and {p.relative_to(ROOT)} ({p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
