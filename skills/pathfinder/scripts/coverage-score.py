#!/usr/bin/env python3
"""Compute test coverage score from journeys.json.

Usage: python3 coverage-score.py [<testDir>/pathfinder/journeys.json]
"""
from __future__ import annotations

import json
import sys

from pathfinder_paths import find_journeys_file


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else find_journeys_file() or "pathfinder/journeys.json"

    with open(path) as f:
        data = json.load(f)

    journeys = data.get("journeys", [])
    seen_ids: set[str] = set()
    total = 0
    tested = 0
    partial = 0
    per_journey: list[dict] = []

    for j in journeys:
        steps = j.get("steps", [])
        j_total = len(steps)
        j_tested = sum(1 for s in steps if s.get("tested") is True)
        j_partial = sum(1 for s in steps if s.get("tested") == "partial")
        cov = round(j_tested / j_total * 100, 1) if j_total else 0
        per_journey.append({"id": j["id"], "name": j["name"], "steps": j_total, "tested": j_tested, "coverage": cov})
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

    overall = round(tested / total * 100, 1) if total else 0

    result = {
        "totalSteps": total,
        "tested": tested,
        "partial": partial,
        "untested": total - tested - partial,
        "coverage": overall,
        "journeys": per_journey,
    }

    print(json.dumps(result, indent=2))

    if overall >= 80:
        print(f"EXCELLENT: {overall}% coverage", file=sys.stderr)
    elif overall >= 50:
        print(f"ACCEPTABLE: {overall}% coverage", file=sys.stderr)
    else:
        print(f"INSUFFICIENT: {overall}% coverage — continue scouting", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
