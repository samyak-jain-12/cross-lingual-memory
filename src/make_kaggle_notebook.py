"""Bundle the tested pipeline (src/clm) and a batch's data into one self-contained Kaggle notebook.

Run from the project root:  python src/make_kaggle_notebook.py batch01_pilot
Output: kaggle/clm_<batch>.ipynb  -> upload in Kaggle via File > Import Notebook.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KROOT = "/kaggle/working/clm"


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip().splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip().splitlines(keepends=True)}


def writefile(dest, content):
    """Embed a file verbatim (no stripping), so the notebook runs exactly the code tested locally."""
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": f"%%writefile {dest}\n{content}".splitlines(keepends=True)}


def build(batch, run=None):
    """batch = which item file to bundle; run = results folder name (defaults to the batch name)."""
    run = run or batch
    items_rel = f"data/items/items_{batch}.jsonl"
    stage = 'stage("{}")'
    cells = [md(f"""
# Cross-Lingual Memory in LLM Agents: {run} (items: {batch})

Runs the experiment pipeline from `phase2/design_spec.md` on Kaggle **GPU T4 x2** (internet on, secret `HF_TOKEN` attached).

| Step | What | Rough time |
|---|---|---|
| 1-3 | Install vLLM, read HF token, write code + data | ~6 min |
| 4 | Translate fillers + build histories + English translations (Qwen3-8B) | ~10 min |
| 5 | Retrieval: BGE-M3, multilingual-E5, BM25 | ~5 min |
| 6 | Token-length check | ~1 min |
| 7 | Reader: Qwen3-8B | ~20-30 min |
| 8 | Reader: Llama-3.1-8B | ~20-30 min |
| 9 | Judge: Qwen3-14B-AWQ | ~15 min |
| 10 | Report + download zip | ~1 min |

Times are estimates until the first run. Every stage caches its outputs: if the session dies, re-run from the top and finished work is skipped.
For an unattended run use **Save Version -> Save & Run All (Commit)**; outputs then appear under the notebook's *Output* tab.
"""),
             md("## 1. Install"),
             code("""
!nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
!pip install -q -U vllm sentence-transformers 2>&1 | tail -2
# vLLM upgrades PyTorch; Kaggle's preinstalled torchaudio then no longer matches and breaks
# `import transformers`. We never use audio, so remove it.
!pip uninstall -y -q torchaudio
import subprocess, os
CHECK = ("import torch, vllm; from vllm import LLM; import transformers; "
         "print('torch', torch.__version__, '| cuda', torch.version.cuda, '| GPUs visible:', torch.cuda.device_count(), "
         "'| vllm', vllm.__version__, '| transformers', transformers.__version__); "
         "assert torch.cuda.device_count() == 2, 'PyTorch cannot see both T4 GPUs'")
r = subprocess.run(["python", "-c", CHECK], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-1500:])
if r.returncode != 0:
    raise RuntimeError("STOP: environment check failed (see message above). Copy it to Claude.")
os.environ["CLM_BACKEND"] = "vllm"
print("Environment OK -> backend vllm")
"""),
             md("## 2. Hugging Face token (from Kaggle Secrets; never printed)"),
             code("""
from kaggle_secrets import UserSecretsClient
os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")
os.environ["HUGGING_FACE_HUB_TOKEN"] = os.environ["HF_TOKEN"]
print("HF token loaded:", bool(os.environ["HF_TOKEN"]))
"""),
             md("## 3. Write pipeline code and data"),
             code(f"!mkdir -p {KROOT}/src/clm {KROOT}/data/items {KROOT}/data/haystacks")]
    for p in sorted((ROOT / "src/clm").glob("*.py")):
        cells.append(writefile(f"{KROOT}/src/clm/{p.name}", p.read_text(encoding="utf-8")))
    for rel in (items_rel, "data/haystacks/filler_pool_en.jsonl"):
        cells.append(writefile(f"{KROOT}/{rel}", (ROOT / rel).read_text(encoding="utf-8")))
    cells += [
        md("## 3b. Stage runner (stops Run All if a stage fails)"),
        code(f"""
def stage(name, extra=""):
    ip = get_ipython()
    ip.system(f"cd {KROOT}/src && CLM_ROOT={KROOT} CLM_RUN={run} CLM_BACKEND={{os.environ['CLM_BACKEND']}} "
              f"python -m clm.stages {{name}} --items {KROOT}/{items_rel} {{extra}}")
    if ip.user_ns.get("_exit_code", 0) != 0:
        raise RuntimeError(f"Stage '{{name}}' failed - copy the error above to Claude.")
    print(f"stage {{name}}: done")
"""),
        md("## 4. Translate fillers, build histories, translate memories/queries to English"),
        code(stage.format("translate")),
        md("## 5. Retrieval"),
        code(stage.format("retrieve")),
        md("## 6. Token-length check (Hindi/Hinglish need more tokens)"),
        code(stage.format("tokens")),
        md("## 7. Reader: Qwen3-8B (then free disk)"),
        code('stage("generate", "--model qwen3-8b")\n!rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen3-8B'),
        md("## 8. Reader: Llama-3.1-8B-Instruct (then free disk)"),
        code('stage("generate", "--model llama3.1-8b")\n!rm -rf ~/.cache/huggingface/hub/models--meta-llama--Llama-3.1-8B-Instruct'),
        md("## 9. Judge: Qwen3-14B-AWQ"),
        code(stage.format("judge")),
        md("## 10. Report and download"),
        code(stage.format("report") + f"""
import shutil
shutil.make_archive("/kaggle/working/results_{run}", "zip", "{KROOT}/results/{run}")
print("Download: /kaggle/working/results_{run}.zip  (right panel -> Output)")
"""),
    ]
    nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                       "language_info": {"name": "python"},
                                       "kaggle": {"accelerator": "nvidiaTeslaT4", "isInternetEnabled": True}},
          "nbformat": 4, "nbformat_minor": 4}
    out = ROOT / "kaggle" / f"clm_{run}.ipynb"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({len(cells)} cells, {out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "batch01_pilot", sys.argv[2] if len(sys.argv) > 2 else None)
