#!/usr/bin/env python3
"""Triggering eval: does the skill fire when it should and stay quiet otherwise?

For each query it runs Claude Code headless with the Pathfinder skills available
and detects whether a skill actually fired (from the stream-json tool events). A
query "passes" when the observed trigger rate matches expectation at the 0.5
threshold. Reports accuracy plus a held-out test split to guard against a
description that's overfit to a few phrasings.

Needs the ``claude`` CLI logged in. Pure logic (split, rate, metrics) is unit-tested.

Usage:
  python3 run_triggering.py --runs 3
  python3 run_triggering.py --runs 1 --query-id t01
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from _common import (
    EVALS_DIR,
    REPO_ROOT,
    RUNS_DIR,
    SKILL_NAMES,
    ModelUnavailable,
    claude_flags,
    have_command,
    load_json,
    model_unavailable,
    write_json,
)


def detect_trigger(stream_text: str, skill_names: list[str]) -> bool:
    """True if a Pathfinder skill fired — i.e. a `Skill` tool_use that targets our
    plugin. Loaded via --plugin-dir, our skills register as `pathfinder:<name>`, so we
    match the plugin-namespaced identifiers (and the bare `pathfinder` namespace),
    NOT the generic bare names like "map"/"scout" which collide with ordinary words
    that may appear in an unrelated skill's arguments."""
    needles = [f"pathfinder:{n.lower()}" for n in skill_names] + ["pathfinder"]
    for line in stream_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = event.get("message") or {}
        content = msg.get("content") if isinstance(msg, dict) else None
        for blk in content or []:
            if isinstance(blk, dict) and blk.get("type") == "tool_use" and blk.get("name") == "Skill":
                # Match against the invoked skill identifier only, not the whole event.
                inp = blk.get("input") or {}
                target = " ".join(str(inp.get(k, "")) for k in ("command", "name", "skill")).lower()
                if not target.strip():
                    target = json.dumps(inp).lower()
                if any(n in target for n in needles):
                    return True
    return False


def run_query_once(query: str, timeout: int = 90, model: str = "sonnet",
                   plugin_dir: Path = REPO_ROOT) -> bool:
    """Run one query headless with the Pathfinder plugin loaded; return whether a
    skill fired. The plugin is loaded via --plugin-dir (headless ignores a project's
    .claude/skills/). Model is pinned so we don't inherit an unavailable session model."""
    with tempfile.TemporaryDirectory(prefix="pf-trig-") as tmp:
        project = Path(tmp)
        cmd = ["claude", "-p", query, "--model", model, "--output-format", "stream-json",
               "--verbose", "--max-turns", "4", "--plugin-dir", str(plugin_dir)] + claude_flags()
        try:
            proc = subprocess.run(cmd, cwd=str(project), capture_output=True,
                                  text=True, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            return detect_trigger(e.stdout or "", SKILL_NAMES)
        # A model outage (session/usage limit) must NOT be recorded as "didn't fire".
        if model_unavailable(proc.stdout) or model_unavailable(proc.stderr):
            raise ModelUnavailable("backend model unavailable (session/usage limit?) "
                                   "while running a triggering query")
        return detect_trigger(proc.stdout, SKILL_NAMES)


def trigger_rate(observations: list[bool]) -> float:
    return round(sum(1 for o in observations if o) / len(observations), 3) if observations else 0.0


def query_passed(should_trigger: bool, rate: float, threshold: float = 0.5) -> bool:
    return rate >= threshold if should_trigger else rate < threshold


def split_train_test(queries: list[dict], train_frac: float = 0.6) -> tuple[list[dict], list[dict]]:
    """Deterministic stratified split by should_trigger (no RNG, reproducible)."""
    train, test = [], []
    for cls in (True, False):
        group = sorted([q for q in queries if q.get("should_trigger") is cls], key=lambda q: q["id"])
        cut = round(len(group) * train_frac)
        train += group[:cut]
        test += group[cut:]
    return train, test


def metrics(results: list[dict]) -> dict:
    """Confusion-matrix metrics over graded query results."""
    tp = sum(1 for r in results if r["should_trigger"] and r["fired"])
    fn = sum(1 for r in results if r["should_trigger"] and not r["fired"])
    fp = sum(1 for r in results if not r["should_trigger"] and r["fired"])
    tn = sum(1 for r in results if not r["should_trigger"] and not r["fired"])
    total = len(results) or 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return {
        "accuracy": round((tp + tn) / total, 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "passed": sum(1 for r in results if r["passed"]),
        "total": len(results),
        "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pathfinder triggering eval")
    parser.add_argument("--runs", type=int, default=3, help="Runs per query")
    parser.add_argument("--query-id", help="Run only this query id")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--model", default="sonnet", help="Model id/alias (pinned, default sonnet)")
    parser.add_argument("--out", help="Output dir (default: evals/runs/triggering-<ts>)")
    args = parser.parse_args()

    if not have_command("claude"):
        print("ERROR: triggering eval needs the 'claude' CLI logged in.", file=sys.stderr)
        return 2

    suite = load_json(EVALS_DIR / "triggering.json")
    queries = suite["queries"]
    if args.query_id:
        queries = [q for q in queries if q["id"] == args.query_id]

    out_dir = Path(args.out) if args.out else RUNS_DIR / f"triggering-{time.strftime('%Y%m%d-%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    try:
        for q in queries:
            obs = [run_query_once(q["query"], model=args.model) for _ in range(args.runs)]
            rate = trigger_rate(obs)
            fired = rate >= args.threshold
            passed = query_passed(q["should_trigger"], rate, args.threshold)
            mark = "✓" if passed else "✗"
            print(f"  {mark} [{q['id']}] should={q['should_trigger']} rate={rate:.0%} {q['query'][:60]}")
            results.append({"id": q["id"], "query": q["query"], "should_trigger": q["should_trigger"],
                            "trigger_rate": rate, "fired": fired, "passed": passed})
    except ModelUnavailable as exc:
        print(f"\nABORTED: {exc}\n  Re-run when the model is available; no misleading "
              f"report was written.", file=sys.stderr)
        return 2

    overall = metrics(results)
    train, test = split_train_test(queries)
    train_ids, test_ids = {q["id"] for q in train}, {q["id"] for q in test}
    test_metrics = metrics([r for r in results if r["id"] in test_ids]) if len(queries) > 1 else overall

    report = {"runs_per_query": args.runs, "threshold": args.threshold,
              "overall": overall, "held_out_test": test_metrics,
              "train_ids": sorted(train_ids), "test_ids": sorted(test_ids),
              "results": results}
    write_json(out_dir / "triggering_report.json", report)

    print(f"\nOverall: {overall['passed']}/{overall['total']} passed | "
          f"accuracy {overall['accuracy']:.0%} | precision {overall['precision']:.0%} | "
          f"recall {overall['recall']:.0%}")
    print(f"Report: {out_dir}/triggering_report.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
