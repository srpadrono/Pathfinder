#!/usr/bin/env python3
"""Validate the structure of a journeys.json file.

Usage: python3 validate-journeys.py <path-to-journeys.json>

Outputs JSON to stdout: {"valid": true/false, "errors": [...], "warnings": [...], "stats": {...}}
"""
from __future__ import annotations

import argparse
import json
import re
import sys

VALID_TESTED_VALUES = {True, False, "partial"}
STEP_ID_PATTERN = re.compile(r'^[A-Z]+-\d{2}$')
REQUIRED_TOP_LEVEL = {"journeys"}
OPTIONAL_TOP_LEVEL = {"version", "project", "framework"}
ALLOWED_TOP_LEVEL = REQUIRED_TOP_LEVEL | OPTIONAL_TOP_LEVEL


def validate(data: dict) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    total_steps = 0
    seen_journey_ids: set[str] = set()

    # Check top-level fields
    if not isinstance(data, dict):
        errors.append("Top-level value must be a JSON object")
        return errors, warnings, 0

    if "journeys" not in data:
        errors.append("Missing required top-level field: journeys")
        return errors, warnings, 0

    if not isinstance(data["journeys"], list):
        errors.append("\"journeys\" must be an array")
        return errors, warnings, 0

    for ji, journey in enumerate(data["journeys"]):
        prefix = f"journey[{ji}]"

        if not isinstance(journey, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        # Required journey fields
        for field in ("id", "name", "steps"):
            if field not in journey:
                errors.append(f"{prefix}: missing required field \"{field}\"")

        jid = journey.get("id")
        if jid is not None:
            if not isinstance(jid, str):
                errors.append(f"{prefix}: \"id\" must be a string")
            elif jid in seen_journey_ids:
                errors.append(f"{prefix}: duplicate journey id \"{jid}\"")
            else:
                seen_journey_ids.add(jid)

        if "name" in journey and not isinstance(journey["name"], str):
            errors.append(f"{prefix}: \"name\" must be a string")

        steps = journey.get("steps")
        if steps is not None:
            if not isinstance(steps, list):
                errors.append(f"{prefix}: \"steps\" must be an array")
                continue
            if len(steps) == 0:
                errors.append(f"{prefix}: \"steps\" must not be empty")
                continue

            seen_step_ids_in_journey: set[str] = set()
            for si, step in enumerate(steps):
                sp = f"{prefix}.steps[{si}]"
                total_steps += 1

                if not isinstance(step, dict):
                    errors.append(f"{sp}: must be an object")
                    continue

                for field in ("id", "action", "screen"):
                    if field not in step:
                        errors.append(f"{sp}: missing required field \"{field}\"")

                sid = step.get("id")
                if sid is not None:
                    if not isinstance(sid, str):
                        errors.append(f"{sp}: \"id\" must be a string")
                    elif not STEP_ID_PATTERN.match(sid):
                        errors.append(f"{sp}: \"id\" must match PREFIX-NN pattern (got \"{sid}\")")
                    elif sid in seen_step_ids_in_journey:
                        errors.append(f"{sp}: duplicate step id \"{sid}\"")
                    else:
                        seen_step_ids_in_journey.add(sid)

                if "action" in step and not isinstance(step["action"], str):
                    errors.append(f"{sp}: \"action\" must be a string")

                if "screen" in step and not isinstance(step["screen"], str):
                    errors.append(f"{sp}: \"screen\" must be a string")

                if "tested" not in step:
                    errors.append(f"{sp}: missing required field \"tested\"")
                else:
                    tested = step["tested"]
                    if tested not in VALID_TESTED_VALUES:
                        errors.append(
                            f"{sp}: \"tested\" must be true, false,"
                            f" or \"partial\" (got {json.dumps(tested)})"
                        )
                    elif tested == "partial" and "note" not in step:
                        warnings.append(f"{sp}: tested is \"partial\" but no \"note\" field provided")

    return errors, warnings, total_steps


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a journeys.json file")
    parser.add_argument("path", help="Path to journeys.json")
    args = parser.parse_args()

    # Read and parse JSON
    try:
        with open(args.path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {args.path}", file=sys.stderr)
        print(json.dumps({
            "valid": False,
            "errors": [f"File not found: {args.path}"],
            "warnings": [],
            "stats": {"journeys": 0, "steps": 0},
        }, indent=2))
        sys.exit(1)
    except json.JSONDecodeError as e:
        msg = f"Invalid JSON: {e.msg} (line {e.lineno}, col {e.colno})"
        print(f"ERROR: {msg}", file=sys.stderr)
        print(json.dumps({
            "valid": False,
            "errors": [msg],
            "warnings": [],
            "stats": {"journeys": 0, "steps": 0},
        }, indent=2))
        sys.exit(1)

    errors, warnings, total_steps = validate(data)
    journey_count = len(data.get("journeys", []))

    valid = len(errors) == 0
    result = {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "journeys": journey_count,
            "steps": total_steps,
        },
    }

    print(json.dumps(result, indent=2))

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    if warnings:
        for w in warnings:
            print(f"WARNING: {w}", file=sys.stderr)


if __name__ == "__main__":
    main()
