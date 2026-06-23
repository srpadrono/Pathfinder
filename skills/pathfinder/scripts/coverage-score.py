#!/usr/bin/env python3
"""Compute test coverage score from journeys.json.

Usage:
  python3 coverage-score.py [<testDir>/pathfinder/journeys.json] [--fail-under N]

Exit code is 0 by default (this is a reporting tool). Set a gate with --fail-under
or coverage.failUnder in config.json to make it exit non-zero below a threshold —
useful for CI. Thresholds and whether "partial" steps count toward coverage are
read from config.json (see schema/config.schema.json).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from pathfinder_config import coverage_thresholds, load_config
from pathfinder_paths import find_journeys_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute Pathfinder coverage score")
    parser.add_argument("path", nargs="?", help="Path to journeys.json (auto-detected if omitted)")
    parser.add_argument("--fail-under", type=float, default=None,
                        help="Exit non-zero if overall coverage is below this percent (overrides config).")
    args = parser.parse_args()

    path = args.path or find_journeys_file() or "pathfinder/journeys.json"
    # Root config to the project that owns this journeys.json, not the cwd.
    config = load_config(os.path.dirname(path) or ".")
    count_partial = config.get("coverage", {}).get("countPartialAsTested", False)
    excellent, acceptable = coverage_thresholds(config)
    fail_under = args.fail_under if args.fail_under is not None else config.get("coverage", {}).get("failUnder")

    with open(path) as f:
        data = json.load(f)

    journeys = data.get("journeys", [])
    seen_ids: set[str] = set()
    total = 0
    tested = 0
    partial = 0
    per_journey: list[dict] = []

    def counts_as_covered(step: dict) -> bool:
        v = step.get("tested")
        return v is True or (count_partial and v == "partial")

    for j in journeys:
        steps = j.get("steps", [])
        j_total = len(steps)
        j_covered = sum(1 for s in steps if counts_as_covered(s))
        cov = round(j_covered / j_total * 100, 1) if j_total else 0
        per_journey.append({"id": j.get("id", ""), "name": j.get("name", ""),
                            "steps": j_total, "tested": j_covered, "coverage": cov})
        # Overall totals deduplicate shared step IDs
        for s in steps:
            sid = s.get("id", "")
            if sid not in seen_ids:
                seen_ids.add(sid)
                total += 1
                if s.get("tested") is True:
                    tested += 1
                elif s.get("tested") == "partial":
                    partial += 1

    covered = tested + (partial if count_partial else 0)
    overall = round(covered / total * 100, 1) if total else 0

    result = {
        "totalSteps": total,
        "tested": tested,
        "partial": partial,
        "untested": total - tested - partial,
        "coverage": overall,
        "countPartialAsTested": count_partial,
        "journeys": per_journey,
    }

    print(json.dumps(result, indent=2))

    if overall >= excellent:
        print(f"EXCELLENT: {overall}% coverage", file=sys.stderr)
    elif overall >= acceptable:
        print(f"ACCEPTABLE: {overall}% coverage", file=sys.stderr)
    else:
        print(f"INSUFFICIENT: {overall}% coverage — continue scouting", file=sys.stderr)

    if fail_under is not None and overall < float(fail_under):
        print(f"FAIL: coverage {overall}% is below the {fail_under}% gate", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
