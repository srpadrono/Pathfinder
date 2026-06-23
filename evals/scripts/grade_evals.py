#!/usr/bin/env python3
"""Grade eval runs with an LLM-as-judge against discriminating expectations.

This is the compliant grading path. It needs the ``claude`` CLI logged in (or an
ANTHROPIC_API_KEY for the anthropic backend). It does NOT fake results: every
verdict comes from the judge model, with no partial credit and the burden of
proof on passing (see ../agents/grader.md).

Usage:
  python3 grade_evals.py --run-dir evals/runs/<timestamp>
  python3 grade_evals.py                      # grades the most recent run dir
  python3 grade_evals.py --backend anthropic  # use the Python SDK instead of the CLI
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from _common import (
    EVALS_DIR,
    RUNS_DIR,
    ModelUnavailable,
    claude_flags,
    have_command,
    load_json,
    model_unavailable,
    write_json,
)

GRADER_PROMPT = (EVALS_DIR / "agents" / "grader.md").read_text()


def already_graded(grading_path: Path) -> bool:
    """True if this run already has a non-empty grading (used to resume incrementally)."""
    return grading_path.exists() and bool(load_json(grading_path).get("expectations"))


def latest_run_dir() -> Path | None:
    if not RUNS_DIR.exists():
        return None
    dirs = [d for d in RUNS_DIR.iterdir() if d.is_dir()]
    return max(dirs, key=lambda d: d.stat().st_mtime) if dirs else None


def build_payload(case: dict, transcript: dict, artifacts: dict) -> str:
    lines = [
        "## TASK PROMPT", case["prompt"], "",
        "## EXPECTATIONS (grade each, in order)",
    ]
    for i, e in enumerate(case["expectations"], 1):
        lines.append(f"{i}. [{e['id']}] {e['text']}")
    lines += ["", "## AGENT FINAL RESULT", transcript.get("result_text", "")[:8000], ""]
    lines.append("## ARTIFACTS PRODUCED BY THE AGENT")
    files = artifacts.get("files", {})
    if not files:
        lines.append("(none — the agent produced no files)")
    for path, content in files.items():
        lines.append(f"\n=== {path} ===\n{content[:6000]}")
    lines += ["", "Grade every expectation now. Output ONLY the JSON object described above."]
    return "\n".join(lines)


def extract_json(text: str) -> dict | None:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def judge_claude(payload: str, model: str | None) -> dict | None:
    cmd = ["claude", "-p", payload, "--append-system-prompt", GRADER_PROMPT,
           "--output-format", "json"]
    if model:
        cmd += ["--model", model]
    cmd += claude_flags()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    try:
        result_text = json.loads(proc.stdout).get("result", proc.stdout)
    except json.JSONDecodeError:
        result_text = proc.stdout
    if model_unavailable(result_text) or model_unavailable(proc.stderr):
        raise ModelUnavailable("judge model unavailable (session/usage limit?)")
    return extract_json(result_text)


def judge_anthropic(payload: str, model: str | None) -> dict | None:
    try:
        import anthropic  # type: ignore
    except ImportError:
        raise SystemExit("anthropic SDK not installed. pip install anthropic, or use --backend claude") from None
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=model or "claude-opus-4-8",
        max_tokens=2000,
        system=GRADER_PROMPT,
        messages=[{"role": "user", "content": payload}],
    )
    return extract_json("".join(b.text for b in msg.content if getattr(b, "type", "") == "text"))


def normalize(grading: dict, case: dict) -> dict:
    """Trust the judge's verdicts; recompute the summary defensively."""
    exps = grading.get("expectations", [])
    passed = sum(1 for e in exps if e.get("passed") is True)
    total = len(exps)
    grading["summary"] = {
        "passed": passed, "failed": total - passed, "total": total,
        "pass_rate": round(passed / total, 2) if total else 0.0,
    }
    return grading


def main() -> int:
    parser = argparse.ArgumentParser(description="LLM-judge grading for Pathfinder evals")
    parser.add_argument("--run-dir", help="Run dir to grade (default: most recent)")
    parser.add_argument("--backend", choices=["claude", "anthropic"], default="claude")
    parser.add_argument("--model", help="Judge model id/alias "
                        "(default: $PATHFINDER_EVAL_JUDGE_MODEL or 'opus' — use the most "
                        "capable model to grade).")
    parser.add_argument("--regrade", action="store_true",
                        help="Re-grade runs that already have a grading.json. Default: skip "
                             "already-graded runs so grading resumes incrementally (e.g. across "
                             "usage-limit windows) instead of restarting each time.")
    args = parser.parse_args()

    if not args.model:
        args.model = os.environ.get("PATHFINDER_EVAL_JUDGE_MODEL", "opus")

    if args.backend == "claude" and not have_command("claude"):
        print("ERROR: LLM-judge grading needs the 'claude' CLI logged in (or use --backend "
              "anthropic with ANTHROPIC_API_KEY). No results were faked.", file=sys.stderr)
        return 2
    if args.backend == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: --backend anthropic needs ANTHROPIC_API_KEY.", file=sys.stderr)
        return 2

    run_dir = Path(args.run_dir) if args.run_dir else latest_run_dir()
    if not run_dir or not run_dir.exists():
        print("ERROR: no run dir found. Run run_evals.py first.", file=sys.stderr)
        return 1

    suite = {c["id"]: c for c in load_json(EVALS_DIR / "output_quality.json")["evals"]}
    judge = judge_claude if args.backend == "claude" else judge_anthropic

    graded = 0
    skipped = 0
    try:
        for transcript_path in sorted(run_dir.rglob("transcript.json")):
            transcript = load_json(transcript_path)
            case = suite.get(transcript["eval_id"])
            if not case:
                continue
            grading_path = transcript_path.parent / "grading.json"
            if not args.regrade and already_graded(grading_path):
                skipped += 1
                continue  # resume: leave already-graded runs in place
            artifacts = load_json(transcript_path.parent / "artifacts.json")
            payload = build_payload(case, transcript, artifacts)
            print(f"  grading {transcript['eval_id']} / {transcript['config']} / run {transcript['run']} ...",
                  flush=True)
            grading = judge(payload, args.model)
            if grading is None:
                grading = {"expectations": [], "error": "judge returned no parseable JSON"}
            grading = normalize(grading, case)
            write_json(transcript_path.parent / "grading.json", grading)
            graded += 1
    except ModelUnavailable as exc:
        print(f"\nABORTED: {exc}\n  The judge couldn't run — re-grade later with "
              f"`grade_evals.py --run-dir {run_dir}`. A model outage is not a skill result, "
              f"so no 0% gradings were fabricated.", file=sys.stderr)
        return 2

    msg = f"\nGraded {graded} run(s)"
    if skipped:
        msg += f" ({skipped} already-graded skipped; --regrade to redo)"
    print(f"{msg}. Next: python3 aggregate_benchmark.py --run-dir {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
