"""Endsem (ENDSEM_PLAN.md §3 change 7): build the four Kaggle notebooks for the main study + ablations.

  1_prep   translate (fillers are frozen and bundled), histories + English translations for every block,
           retrieval, token check for both tokenizers                                   (inputs: none)
  2_qwen   reader Qwen3-8B on every block                                               (inputs: output of 1)
  3_llama  reader Llama-3.1-8B on every block                                           (inputs: output of 1)
  4_judge  judge on every block, reports, final zip                                     (inputs: outputs of 1, 2, 3)

Each notebook writes its results under /kaggle/working/clm/results/<run>/ (kept as the notebook's output) and
restores earlier parts from /kaggle/input. Every stage caches its outputs, so a crashed notebook can be re-run.
Run from the project root:  python src/make_main_notebooks.py main_r1
Output: kaggle/<run>_1_prep.ipynb ... kaggle/<run>_4_judge.ipynb
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_kaggle_notebook import code, md, writefile   # noqa: E402  (same cell helpers as the pilot builder)

ROOT = Path(__file__).resolve().parents[1]
KROOT = "/kaggle/working/clm"
ITEMS = "data/items/items_main.jsonl"
BLOCKS = ("main", "short", "q3", "digits")
DATA_FILES = (ITEMS, "data/haystacks/filler_pool_en.jsonl", "data/haystacks/filler_pool_hi.jsonl",
              "data/haystacks/filler_pool_hg.jsonl")
VLLM_VERSION = "0.30.0"   # the version that ran the pilot (results/batch01_pilot_r2/ANALYSIS.md)

PARTS = {
    "1_prep":  {"title": "Part 1 of 4: preparation", "gpu_models": ["Qwen3-8B (translator)"],
                "needs": [], "time": "~45-75 min"},
    "2_qwen":  {"title": "Part 2 of 4: reader Qwen3-8B", "gpu_models": ["Qwen3-8B"],
                "needs": ["1_prep"], "time": "~2-4 h (estimate)"},
    "3_llama": {"title": "Part 3 of 4: reader Llama-3.1-8B", "gpu_models": ["Llama-3.1-8B-Instruct"],
                "needs": ["1_prep"], "time": "~2-4 h (estimate)"},
    "4_judge": {"title": "Part 4 of 4: judge + report", "gpu_models": ["Qwen3-14B-AWQ"],
                "needs": ["1_prep", "2_qwen", "3_llama"], "time": "~1.5-2.5 h (estimate)"},
}

FREE_DISK = ("!rm -rf ~/.cache/huggingface/hub/{models} ~/.cache/huggingface/xet ~/.cache/pip /tmp/*.whl 2>/dev/null; "
             "df -h /kaggle/working | tail -1")


def header(run, part):
    p = PARTS[part]
    needs = ", ".join(f"the output of `{run}_{n}`" for n in p["needs"]) or "nothing"
    return md(f"""
# Cross-Lingual Memory in LLM Agents: `{run}`, {p['title']}

Settings: **GPU T4 x2**, **Internet on**, secret **`HF_TOKEN`** attached (Add-ons → Secrets). Inputs needed: {needs}
(right panel → **Add Input** → *Your Work* → the notebook → its latest version).

Run it unattended with **Save Version → Save & Run All (Commit)**. Rough time: {p['time']}. Every stage caches what it
has finished, so if the session dies, commit again and finished work is skipped. Blocks: `main` (165 items,
20 sessions) and the ablations `short`, `q3`, `digits` (ENDSEM_PLAN.md §1).
""")


def setup_cells(run, part):
    cells = [md("## 1. Install and check the GPUs"),
             code(f"""
!nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
!pip install -q vllm=={VLLM_VERSION} sentence-transformers 2>&1 | tail -2
# vLLM upgrades PyTorch; Kaggle's preinstalled torchaudio then no longer matches and breaks
# `import transformers`. We never use audio, so remove it.
!pip uninstall -y -q torchaudio
import subprocess, os, glob, shutil
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
             md("## 3. Write pipeline code and data (frozen fillers included)"),
             code(f"!mkdir -p {KROOT}/src/clm {KROOT}/data/items {KROOT}/data/haystacks {KROOT}/results/{run}")]
    for p in sorted((ROOT / "src/clm").glob("*.py")):
        cells.append(writefile(f"{KROOT}/src/clm/{p.name}", p.read_text(encoding="utf-8")))
    for rel in DATA_FILES:
        cells.append(writefile(f"{KROOT}/{rel}", (ROOT / rel).read_text(encoding="utf-8")))
    cells += [md("## 4. Restore earlier parts and define the stage runner"),
              code(f"""
RUN, KROOT, ITEMS = "{run}", "{KROOT}", "{KROOT}/{ITEMS}"
RESULTS = f"{{KROOT}}/results/{{RUN}}"
NEEDS = {PARTS[part]["needs"]!r}

# Earlier parts arrive under /kaggle/input/<notebook>/clm/results/<run>/ (or as results_<run>_*.zip).
found = []
for src in sorted(glob.glob(f"/kaggle/input/**/clm/results/{{RUN}}", recursive=True)):
    shutil.copytree(src, RESULTS, dirs_exist_ok=True); found.append(src)
for z in glob.glob(f"/kaggle/input/**/results_{{RUN}}_*.zip", recursive=True):
    shutil.unpack_archive(z, RESULTS); found.append(z)
print("restored from:", found or "nothing")
need_files = {{"1_prep": "histories.jsonl", "2_qwen": "generations_qwen3-8b.jsonl", "3_llama": "generations_llama3.1-8b.jsonl"}}
for n in NEEDS:
    f = need_files[n]
    missing = [b for b in {BLOCKS!r} if not os.path.exists(f"{{RESULTS}}/{{'' if b == 'main' else 'abl_' + b + '/'}}{{f}}")]
    if missing:
        raise RuntimeError(f"STOP: output of part {{RUN}}_{{n}} not found for blocks {{missing}}. "
                           "Add it with Add Input -> Your Work, then run again.")

def stage(name, block, extra=""):
    ip = get_ipython()
    ip.system(f"cd {{KROOT}}/src && CLM_ROOT={{KROOT}} CLM_RUN={{RUN}} CLM_BLOCK={{block}} "
              f"CLM_BACKEND={{os.environ['CLM_BACKEND']}} python -m clm.stages {{name}} --items {{ITEMS}} {{extra}}")
    if ip.user_ns.get("_exit_code", 0) != 0:
        raise RuntimeError(f"Stage '{{name}}' (block {{block}}) failed - copy the error above to Claude.")
    print(f"stage {{name}} / {{block}}: done")
""")]
    return cells


def part_cells(run, part):
    blocks = repr(BLOCKS)
    if part == "1_prep":
        return [
            md("## 5. Histories and English translations (Qwen3-8B translator; HI/HG fillers are frozen, not re-translated)"),
            code(f"for b in {blocks}:\n    stage('translate', b)"),
            md("## 6. Retrieval (BGE-M3, multilingual-E5, BM25), then free the embedders"),
            code(f"for b in {blocks}:\n    stage('retrieve', b)\n"
                 + FREE_DISK.format(models="models--Qwen--Qwen3-8B models--BAAI--bge-m3 models--intfloat--multilingual-e5-large")),
            md("## 7. Token check: every full-context prompt must fit the 32,768-token reader context (both tokenizers)"),
            code(f"for b in {blocks}:\n    stage('tokens', b)\n"
                 "import pandas as pd\nfor b in " + blocks + ":\n"
                 "    p = f\"{RESULTS}/{'' if b == 'main' else 'abl_' + b + '/'}table_tokens.csv\"\n"
                 "    print(b); print(pd.read_csv(p).to_string(index=False))"),
        ]
    if part in ("2_qwen", "3_llama"):
        key, hf = (("qwen3-8b", "models--Qwen--Qwen3-8B") if part == "2_qwen"
                   else ("llama3.1-8b", "models--meta-llama--Llama-3.1-8B-Instruct"))
        return [md(f"## 5. Reader {key}: main block first, then the ablations"),
                code(f"for b in {blocks}:\n    stage('generate', b, '--model {key}')\n" + FREE_DISK.format(models=hf))]
    return [md("## 5. Judge (Qwen3-14B-AWQ) on every block"),
            code(f"for b in {blocks}:\n    stage('judge', b)\n" + FREE_DISK.format(models="models--Qwen--Qwen3-14B-AWQ")),
            md("## 6. Reports (one summary per block)"),
            code(f"for b in {blocks}:\n    stage('report', b)\n"
                 "print(open(f'{RESULTS}/summary.md').read()[:4000])")]


def footer(run, part):
    return [md("## Save outputs"),
            code(f"""
# The whole results folder stays in /kaggle/working and becomes this notebook's output (input for the next part).
shutil.make_archive(f"/kaggle/working/results_{{RUN}}_{part}", "zip", RESULTS)
print("Output folder:", RESULTS)
print(f"Download zip: /kaggle/working/results_{{RUN}}_{part}.zip  (right panel -> Output)")
""")]


def build(run):
    out_dir = ROOT / "kaggle"
    out_dir.mkdir(exist_ok=True)
    for part in PARTS:
        cells = [header(run, part)] + setup_cells(run, part) + part_cells(run, part) + footer(run, part)
        nb = {"cells": cells,
              "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                           "language_info": {"name": "python"},
                           "kaggle": {"accelerator": "nvidiaTeslaT4", "isInternetEnabled": True}},
              "nbformat": 4, "nbformat_minor": 4}
        out = out_dir / f"{run}_{part}.ipynb"
        out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({len(cells)} cells, {out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "main_r1")
