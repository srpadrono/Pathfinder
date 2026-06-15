#!/usr/bin/env python3
"""Run output-quality evals A/B: skill available vs. baseline agent without it.

For each case x configuration x run, this creates an isolated temp project,
stages the fixtures, makes the skill discoverable only in the ``with_skill``
configuration, runs a real agent backend, and saves the transcript + the files
the agent produced. Grading happens separately in grade_evals.py.

Backends:
  claude  Run Claude Code headless (`claude -p`). Needs the CLI logged in.
  codex   Run Codex headless (`codex exec --json`). Needs the CLI logged in.
  mock    No model. Deterministically exercises the harness plumbing so the
          pipeline can be smoke-tested in CI without auth. NOT a quality signal.

Usage:
  python3 run_evals.py --backend claude --runs 3
  python3 run_evals.py --backend claude --eval-id nextjs-playwright-map --runs 1
  python3 run_evals.py --backend mock   # plumbing smoke test
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from _common import (
    EVALS_DIR,
    RUNS_DIR,
    SKILLS_DIR,
    ModelUnavailable,
    claude_plugin_flags,
    have_command,
    install_skills_for_codex,
    load_json,
    run_claude_headless,
    run_codex_headless,
    snapshot_artifacts,
    stage_fixtures,
    write_json,
)

CONFIGS = ["with_skill", "without_skill"]


def _run_mock(prompt: str, project_dir: Path, with_skill: bool) -> dict:
    """Deterministic stand-in. With the skill, run the bundled scripts to produce
    a coverage artifact; without it, produce nothing. Plumbing only."""
    if not with_skill:
        return {"ok": True, "result_text": "[mock baseline] no skill available", "mock": True}

    notes = ["[mock with_skill] exercised bundled scripts:"]
    journeys = project_dir / "pathfinder" / "journeys.json"
    if journeys.exists():
        score = subprocess.run(
            ["python3", str(SKILLS_DIR / "pathfinder" / "scripts" / "coverage-score.py"), str(journeys)],
            cwd=str(project_dir), capture_output=True, text=True,
        )
        notes.append(f"coverage-score exit={score.returncode}: {score.stdout[:200]}")
    detect = subprocess.run(
        ["python3", str(SKILLS_DIR / "pathfinder" / "scripts" / "detect-ui-framework.py"), str(project_dir)],
        cwd=str(project_dir), capture_output=True, text=True,
    )
    notes.append(f"detect-ui-framework exit={detect.returncode}: {detect.stdout[:200]}")
    return {"ok": True, "result_text": "\n".join(notes), "mock": True}


def run_one(case: dict, config: str, run_idx: int, backend: str, model: str | None,
            out_root: Path) -> dict:
    with_skill = config == "with_skill"
    run_dir = out_root / case["id"] / config / f"run-{run_idx}"
    run_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="pf-eval-") as tmp:
        project = Path(tmp)
        stage_fixtures(case, project)
        extra_flags = None
        if with_skill:
            if backend == "codex":
                install_skills_for_codex(project)
            elif backend == "claude":
                extra_flags = claude_plugin_flags()  # headless loads the skill via --plugin-dir

        start = time.time()
        if backend == "claude":
            result = run_claude_headless(case["prompt"], project, model=model, extra_flags=extra_flags)
        elif backend == "codex":
            result = run_codex_headless(case["prompt"], project)
        elif backend == "mock":
            result = _run_mock(case["prompt"], project, with_skill)
        else:
            raise SystemExit(f"unknown backend: {backend}")
        if result.get("unavailable"):
            raise ModelUnavailable(
                f"{case['id']}/{config}: backend model unavailable (session/usage limit?). "
                f"Aborting — refusing to record this as a skill result. Detail: "
                f"{(result.get('result_text') or '')[:160]}")
        duration_ms = result.get("duration_ms") or int((time.time() - start) * 1000)

        artifacts = snapshot_artifacts(project)

    transcript = {
        "eval_id": case["id"],
        "config": config,
        "run": run_idx,
        "backend": backend,
        "prompt": case["prompt"],
        "result_text": result.get("result_text", ""),
        "ok": result.get("ok"),
        "exit_code": result.get("exit_code"),
        "stderr": result.get("stderr"),
    }
    write_json(run_dir / "transcript.json", transcript)
    write_json(run_dir / "artifacts.json", {"files": artifacts})
    write_json(run_dir / "timing.json", {
        "duration_ms": duration_ms,
        "total_cost_usd": result.get("total_cost_usd"),
        "num_turns": result.get("num_turns"),
    })
    return {"eval_id": case["id"], "config": config, "run": run_idx,
            "ok": result.get("ok"), "artifact_count": len(artifacts), "duration_ms": duration_ms}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Pathfinder output-quality evals (A/B)")
    parser.add_argument("--backend", choices=["claude", "codex", "mock"], default="claude")
    parser.add_argument("--runs", type=int, default=3, help="Runs per configuration (variance)")
    parser.add_argument("--eval-id", help="Run only this case id")
    parser.add_argument("--configs", default="with_skill,without_skill",
                        help="Comma-separated subset of with_skill,without_skill")
    parser.add_argument("--model", help="Model id/alias for the agent backend "
                        "(default: $PATHFINDER_EVAL_MODEL or 'sonnet'). Pinned so headless "
                        "runs don't inherit an unavailable session model.")
    parser.add_argument("--out", help="Output dir (default: evals/runs/<timestamp>)")
    args = parser.parse_args()

    if args.backend == "claude" and not args.model:
        args.model = os.environ.get("PATHFINDER_EVAL_MODEL", "sonnet")

    if args.backend == "claude" and not have_command("claude"):
        print("ERROR: the 'claude' CLI is not installed/logged in. Use --backend mock for a "
              "plumbing smoke test, or install Claude Code.", file=sys.stderr)
        return 2
    if args.backend == "codex" and not have_command("codex"):
        print("ERROR: the 'codex' CLI is not installed/logged in.", file=sys.stderr)
        return 2

    suite = load_json(EVALS_DIR / "output_quality.json")
    cases = suite["evals"]
    if args.eval_id:
        cases = [c for c in cases if c["id"] == args.eval_id]
        if not cases:
            print(f"ERROR: no case with id '{args.eval_id}'", file=sys.stderr)
            return 1

    configs = [c for c in args.configs.split(",") if c in CONFIGS]
    out_root = Path(args.out) if args.out else RUNS_DIR / time.strftime("%Y%m%d-%H%M%S")
    out_root.mkdir(parents=True, exist_ok=True)

    print(f"Backend: {args.backend} | cases: {len(cases)} | configs: {configs} | runs: {args.runs}")
    print(f"Output:  {out_root}\n")
    if args.backend == "mock":
        print("NOTE: mock backend tests harness plumbing only — it is not a measure of skill quality.\n")

    summary = []
    try:
        for case in cases:
            for config in configs:
                for run_idx in range(1, args.runs + 1):
                    print(f"  • {case['id']} / {config} / run {run_idx} ...", flush=True)
                    summary.append(run_one(case, config, run_idx, args.backend, args.model, out_root))
    except ModelUnavailable as exc:
        print(f"\nABORTED: {exc}\n  Re-run when the model is available; no misleading "
              f"results were recorded.", file=sys.stderr)
        return 2

    write_json(out_root / "run_summary.json", {
        "backend": args.backend, "runs_per_config": args.runs,
        "configs": configs, "cases": [c["id"] for c in cases], "results": summary,
    })
    print(f"\nDone. Next: python3 grade_evals.py --run-dir {out_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
