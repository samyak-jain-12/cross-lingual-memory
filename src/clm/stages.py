"""Command-line entry point. Each GPU stage runs in its own process so GPU memory is fully released.

  python -m clm.stages translate --items data/items/items_batch01_pilot.jsonl
  python -m clm.stages retrieve  --items ...
  python -m clm.stages tokens    --items ...
  python -m clm.stages generate  --items ... --model qwen3-8b
  python -m clm.stages generate  --items ... --model llama3.1-8b
  python -m clm.stages judge     --items ...
  python -m clm.stages report    --items ...
Set CLM_BACKEND=mock to test the whole pipeline on a CPU; CLM_RUN names the results folder.
"""
import argparse

from . import config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["translate", "retrieve", "tokens", "generate", "judge", "report"])
    ap.add_argument("--items", required=True)
    ap.add_argument("--model", default=None)
    ap.add_argument("--backend", default=None, help="vllm | hf | mock (default: env CLM_BACKEND or vllm)")
    ap.add_argument("--setups", default=",".join(config.SETUPS))
    a = ap.parse_args()
    config.RESULTS.mkdir(parents=True, exist_ok=True)
    if a.stage == "translate":
        from . import translate
        translate.run(a.items, a.backend)
    elif a.stage == "retrieve":
        from . import retrieve
        retrieve.run(a.items)
    elif a.stage == "tokens":
        from . import tokens
        tokens.run(a.items)
    elif a.stage == "generate":
        from . import generate
        generate.run(a.items, a.model, a.backend, tuple(a.setups.split(",")))
    elif a.stage == "judge":
        from . import judge
        judge.run(a.items, a.backend)
    elif a.stage == "report":
        from . import report
        report.run(a.items)


if __name__ == "__main__":
    main()
