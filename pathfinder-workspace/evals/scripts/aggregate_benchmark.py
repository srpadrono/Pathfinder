#!/usr/bin/env python3
"""Aggregate eval results into a benchmark report.

Reads grading.json and timing.json from each eval directory and produces
benchmark.json and benchmark.md summarizing pass rates, timing, and
per-eval breakdowns.

Usage:
    python aggregate_benchmark.py [--iteration N]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent.parent  # pathfinder-workspace/evals/
WORKSPACE = EVALS_DIR.parent  # pathfinder-workspace/


def load_evals() -> dict:
    evals_json = EVALS_DIR / "evals.json"
    with open(evals_json) as f:
        return json.load(f)


def collect_iteration_data(iteration_dir: Path, evals: list[dict]) -> list[dict]:
    """Collect grading and timing data for all evals in an iteration."""
    results = []

    for eval_case in evals:
        eval_name = eval_case.get("name", f"eval-{eval_case['id']}")
        eval_dir = iteration_dir / f"eval-{eval_case['id']}-{eval_name}"

        entry = {
            "eval_id": eval_case["id"],
            "eval_name": eval_name,
            "prompt": eval_case["prompt"][:100],
            "grading": None,
            "timing": None,
        }

        grading_file = eval_dir / "grading.json"
        if grading_file.exists():
            with open(grading_file) as f:
                entry["grading"] = json.load(f)

        timing_file = eval_dir / "with_skill" / "timing.json"
        if timing_file.exists():
            with open(timing_file) as f:
                entry["timing"] = json.load(f)

        results.append(entry)

    return results


def compute_benchmark(results: list[dict]) -> dict:
    """Compute aggregate benchmark metrics."""
    total_assertions = 0
    passed_assertions = 0
    eval_pass_rates = []
    durations = []

    per_eval = []

    for entry in results:
        eval_data = {
            "eval_id": entry["eval_id"],
            "eval_name": entry["eval_name"],
            "prompt": entry["prompt"],
        }

        if entry["grading"]:
            expectations = entry["grading"].get("expectations", [])
            n_passed = sum(1 for e in expectations if e.get("passed"))
            n_total = len(expectations)
            total_assertions += n_total
            passed_assertions += n_passed
            pass_rate = n_passed / n_total if n_total > 0 else 0
            eval_pass_rates.append(pass_rate)
            eval_data["assertions_passed"] = n_passed
            eval_data["assertions_total"] = n_total
            eval_data["pass_rate"] = round(pass_rate * 100, 1)
        else:
            eval_data["assertions_passed"] = 0
            eval_data["assertions_total"] = 0
            eval_data["pass_rate"] = None

        if entry["timing"]:
            duration = entry["timing"].get("total_duration_seconds", 0)
            durations.append(duration)
            eval_data["duration_seconds"] = duration
        else:
            eval_data["duration_seconds"] = None

        per_eval.append(eval_data)

    overall_pass_rate = passed_assertions / total_assertions if total_assertions > 0 else 0

    benchmark = {
        "skill_name": "pathfinder",
        "summary": {
            "total_evals": len(results),
            "total_assertions": total_assertions,
            "passed_assertions": passed_assertions,
            "overall_pass_rate": round(overall_pass_rate * 100, 1),
            "mean_pass_rate": round(statistics.mean(eval_pass_rates) * 100, 1) if eval_pass_rates else 0,
            "stddev_pass_rate": round(statistics.stdev(eval_pass_rates) * 100, 1) if len(eval_pass_rates) > 1 else 0,
            "mean_duration_seconds": round(statistics.mean(durations), 2) if durations else 0,
            "stddev_duration_seconds": round(statistics.stdev(durations), 2) if len(durations) > 1 else 0,
            "total_duration_seconds": round(sum(durations), 2),
        },
        "per_eval": per_eval,
    }

    return benchmark


def generate_markdown(benchmark: dict) -> str:
    """Generate a markdown benchmark report."""
    s = benchmark["summary"]
    lines = [
        "# Pathfinder Skill Eval Benchmark",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Evals | {s['total_evals']} |",
        f"| Total Assertions | {s['total_assertions']} |",
        f"| Passed Assertions | {s['passed_assertions']} |",
        f"| Overall Pass Rate | {s['overall_pass_rate']}% |",
        f"| Mean Pass Rate | {s['mean_pass_rate']}% +/- {s['stddev_pass_rate']}% |",
        f"| Mean Duration | {s['mean_duration_seconds']}s +/- {s['stddev_duration_seconds']}s |",
        f"| Total Duration | {s['total_duration_seconds']}s |",
        "",
        "## Per-Eval Breakdown",
        "",
        "| ID | Name | Pass Rate | Assertions | Duration |",
        "|----|------|-----------|------------|----------|",
    ]

    for e in benchmark["per_eval"]:
        rate = f"{e['pass_rate']}%" if e["pass_rate"] is not None else "N/A"
        assertions = f"{e['assertions_passed']}/{e['assertions_total']}"
        duration = f"{e['duration_seconds']}s" if e["duration_seconds"] is not None else "N/A"
        lines.append(f"| {e['eval_id']} | {e['eval_name']} | {rate} | {assertions} | {duration} |")

    lines.extend(["", "---", "*Generated by Pathfinder skill eval benchmark*"])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Aggregate Pathfinder eval benchmark")
    parser.add_argument("--iteration", type=int, default=1, help="Iteration number")
    args = parser.parse_args()

    data = load_evals()
    iteration_dir = WORKSPACE / f"iteration-{args.iteration}"

    if not iteration_dir.exists():
        print(f"Error: {iteration_dir} does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Aggregating benchmark for iteration {args.iteration}...")

    results = collect_iteration_data(iteration_dir, data["evals"])
    benchmark = compute_benchmark(results)

    # Save benchmark.json
    benchmark_json = iteration_dir / "benchmark.json"
    with open(benchmark_json, "w") as f:
        json.dump(benchmark, f, indent=2)
    print(f"  Saved: {benchmark_json}")

    # Save benchmark.md
    markdown = generate_markdown(benchmark)
    benchmark_md = iteration_dir / "benchmark.md"
    with open(benchmark_md, "w") as f:
        f.write(markdown)
    print(f"  Saved: {benchmark_md}")

    # Print summary
    s = benchmark["summary"]
    print(f"\n  Overall Pass Rate: {s['overall_pass_rate']}%")
    print(f"  Assertions: {s['passed_assertions']}/{s['total_assertions']}")
    print(f"  Duration: {s['total_duration_seconds']}s")


if __name__ == "__main__":
    main()
