"""Independent-model verification (ENDSEM_PLAN status 21 Nov): a second model from a different family
(Cohere Aya Expanse 8B; the judge is Qwen, the readers are Qwen and Llama) re-checks
  1. the LLM judge: 300 answers, stratified by the Qwen judge's label, re-labelled with the judge's exact prompt;
  2. the Hindi / Hinglish items: each translated item audited against its English source.
This is reported in the paper as independent-model verification, not human verification.

Run from the project root:  python3 src/make_verify.py main_r1
Writes data/verify/{judge_keys.json, judge_sample.jsonl, item_audit.jsonl} and kaggle/verify_aya.ipynb.
The notebook is small: it embeds src/verify_build.py and the 300 answer keys, rebuilds the prompts on Kaggle from the
output of `clm-<run>-4-judge` (add it as input), and stops unless the rebuilt files match the local ones (sha256).
"""
import hashlib
import json
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from clm import prompts  # noqa: E402
from make_kaggle_notebook import code, md, writefile  # noqa: E402
import verify_build as vb  # noqa: E402

RUN = sys.argv[1] if len(sys.argv) > 1 else "main_r1"
MODEL = "CohereLabs/aya-expanse-8b"
VLLM_VERSION = "0.30.0"
OUT = ROOT / "data" / "verify"
SEED = 20261121


def select_keys(d):
    """300 answer keys, stratified by the Qwen judge's label and spread over model x setup x cell."""
    rng = random.Random(SEED)

    def spread(pool, n):
        groups = [list(g.index) for _, g in pool.groupby(["model", "setup", "store", "query"])]
        for g in groups:
            rng.shuffle(g)
        rng.shuffle(groups)
        out, k = [], 0
        while len(out) < n and any(groups):
            g = groups[k % len(groups)]
            if g:
                out.append(g.pop())
            k += 1
        return out

    ans, ctl = d[d["answerable"]], d[~d["answerable"]]
    idx = (spread(ans[ans["judge"] == "CORRECT"], 126) + spread(ans[ans["judge"] == "INCORRECT"], 63)
           + spread(ans[ans["judge"] == "NO_ANSWER"], 63)
           + spread(ctl[ctl["judge"] == "ANSWERED"], 24) + spread(ctl[ctl["judge"] == "NO_ANSWER"], 24))
    return [[str(d.loc[i, c]) for c in vb.KEY_COLS] for i in idx]


RUNNER = f'''"""Run Aya Expanse 8B on both verification sets (greedy, fp16, 2xT4)."""
import json, time
from vllm import LLM, SamplingParams

llm = LLM(model="{MODEL}", dtype="half", tensor_parallel_size=2, max_model_len=4096,
          gpu_memory_utilization=0.88, seed=0)

def run(inp, out, max_tokens):
    rows = [json.loads(l) for l in open(inp, encoding="utf-8")]
    t = time.time()
    res = llm.chat([r["messages"] for r in rows], SamplingParams(temperature=0.0, max_tokens=max_tokens), use_tqdm=True)
    with open(out, "w", encoding="utf-8") as f:
        for r, o in zip(rows, res):
            r = {{k: v for k, v in r.items() if k != "messages"}}
            r["aya_raw"] = o.outputs[0].text.strip()
            f.write(json.dumps(r, ensure_ascii=False) + "\\n")
    print(f"{{out}}: {{len(rows)}} rows in {{time.time() - t:.0f}}s")

run("/kaggle/working/verify/judge_sample.jsonl", "/kaggle/working/verify/aya_judge.jsonl", 16)
run("/kaggle/working/verify/item_audit.jsonl", "/kaggle/working/verify/aya_audit.jsonl", 300)
'''


def notebook(keys_json, sha_judge, sha_audit):
    cells = [
        md(f"""
# Cross-Lingual Memory: independent-model verification (`{RUN}`)

A second model from a different family, **{MODEL}**, re-labels 300 judge decisions and audits all 165 items'
Hindi/Hinglish text against the English source. Settings: **GPU T4 x2**, **Internet on**, secret **`HF_TOKEN`**
(the HF account must have accepted the Aya licence). Input: the output of **`clm-{RUN.replace('_', '-')}-4-judge`**.
Run with **Save Version → Save & Run All**.
"""),
        md("## 1. Install and check"),
        code(f"""
!nvidia-smi --query-gpu=name,memory.total --format=csv
!pip install -q vllm=={VLLM_VERSION} 2>&1 | tail -2
!pip uninstall -y -q torchaudio
import os, sys, glob, json, hashlib, subprocess, shutil
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
try:
    hf_hub_download("{MODEL}", "config.json", token=os.environ["HF_TOKEN"]); print("Aya access: OK")
except Exception as e:
    raise RuntimeError("STOP: no access to {MODEL}. Accept its licence on huggingface.co with the HF_TOKEN account. " + str(e)[:300])
"""),
        md("## 2. Rebuild the verification inputs from part 4's output"),
        code("!mkdir -p /kaggle/working/verify"),
        writefile("/kaggle/working/verify/verify_build.py", (ROOT / "src" / "verify_build.py").read_text(encoding="utf-8")),
        writefile("/kaggle/working/verify/judge_keys.json", keys_json),
        writefile("/kaggle/working/verify/run_aya.py", RUNNER),
        code(f"""
hits = glob.glob("/kaggle/input/**/clm/src/clm/prompts.py", recursive=True)
if not hits:
    raise RuntimeError("STOP: add the output of clm-{RUN.replace('_', '-')}-4-judge as input (Add Input -> Your Work)")
CLM = hits[0].rsplit("/src/clm/prompts.py", 1)[0]
print("clm root:", CLM)
sys.path[:0] = [CLM + "/src", "/kaggle/working/verify"]
import pandas as pd
from clm import prompts
import verify_build as vb
items = {{j["item_id"]: j for j in map(json.loads, open(CLM + "/data/items/items_main.jsonl", encoding="utf-8"))}}
scored = pd.read_csv(CLM + "/results/{RUN}/scored.csv")
keys = json.load(open("/kaggle/working/verify/judge_keys.json"))
J = vb.dumps(vb.judge_rows(keys, scored, items, prompts))
A = vb.dumps(vb.audit_rows(items))
for name, text, want in (("judge_sample", J, "{sha_judge}"), ("item_audit", A, "{sha_audit}")):
    got = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print(name, text.count("\\n"), "rows, sha256 match:", got == want)
    if got != want:
        raise RuntimeError(f"STOP: {{name}} differs from the locally built file")
    open(f"/kaggle/working/verify/{{name}}.jsonl", "w", encoding="utf-8").write(text)
"""),
        md("## 3. Run Aya (separate process so the GPUs are released cleanly)"),
        code("""
r = subprocess.run(["python", "/kaggle/working/verify/run_aya.py"], capture_output=True, text=True)
print(r.stdout[-3000:])
if r.returncode != 0:
    print(r.stderr[-5000:]); raise RuntimeError("STOP: Aya run failed (see above)")
"""),
        md("## 4. Quick look and save"),
        code("""
for f in ("aya_judge", "aya_audit"):
    rows = [json.loads(l) for l in open(f"/kaggle/working/verify/{f}.jsonl", encoding="utf-8")]
    print(f, len(rows))
    for x in rows[:3]:
        print("  ", x["aya_raw"][:160].replace("\\n", " "))
shutil.make_archive("/kaggle/working/verify_aya_results", "zip", "/kaggle/working/verify")
print("Download zip: /kaggle/working/verify_aya_results.zip (Output tab)")
"""),
    ]
    return {"cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                         "language_info": {"name": "python"},
                         "kaggle": {"accelerator": "nvidiaTeslaT4", "isInternetEnabled": True}},
            "nbformat": 4, "nbformat_minor": 4}


def flat_cell(nb):
    """The same notebook as one code cell (for pasting into the Kaggle editor): %%writefile cells become writes of
    string literals; everything else is concatenated in order."""
    parts = ["# Cross-Lingual Memory: independent-model verification (Aya Expanse 8B). Generated by src/make_verify.py",
             "import os, sys, glob, json, hashlib, subprocess, shutil"]
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        s = "".join(c["source"])
        if s.startswith("%%writefile"):
            head, body = s.split("\n", 1)
            parts.append(f"open({head.split(' ', 1)[1]!r}, 'w', encoding='utf-8').write({body!r})")
        else:
            parts.append(s.strip())
    return "\n\n".join(parts) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    items = {j["item_id"]: j for j in map(json.loads, open(ROOT / "data/items/items_main.jsonl", encoding="utf-8"))}
    scored = pd.read_csv(ROOT / "results" / RUN / "scored.csv")
    keys = select_keys(scored)
    keys_json = json.dumps(keys, ensure_ascii=False) + "\n"
    J = vb.dumps(vb.judge_rows(keys, scored, items, prompts))
    A = vb.dumps(vb.audit_rows(items))
    (OUT / "judge_keys.json").write_text(keys_json, encoding="utf-8")
    (OUT / "judge_sample.jsonl").write_text(J, encoding="utf-8")
    (OUT / "item_audit.jsonl").write_text(A, encoding="utf-8")
    sha = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()  # noqa: E731
    nb = notebook(keys_json, sha(J), sha(A))
    p = ROOT / "kaggle" / "verify_aya.ipynb"
    p.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "kaggle" / "verify_aya_cell.py").write_text(flat_cell(nb), encoding="utf-8")
    js =[json.loads(l) for l in J.splitlines()]
    print(f"judge sample: {len(js)}; qwen labels {pd.Series([r['qwen_judge'] for r in js]).value_counts().to_dict()}")
    print(f"item audit: {A.count(chr(10))} tasks; sha256 judge {sha(J)[:12]} audit {sha(A)[:12]}")
    print(f"wrote {p.relative_to(ROOT)} ({p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
