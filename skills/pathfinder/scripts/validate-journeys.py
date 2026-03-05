#!/usr/bin/env python3
"""Validate the structure of a journeys.json file.

Usage: python3 validate-journeys.py <path-to-journeys.json>

Outputs JSON to stdout: {"valid": true/false, "errors": [...], "warnings": [...], "stats": {...}}
"""
import argparse, json, re, sys


VALID_TESTED_VALUES = {True, False, "partial"}
STEP_ID_PATTERN = re.compile(r'^[A-Z]+-\d{2}$')
REQUIRED_TOP_LEVEL = {"journeys"}
OPTIONAL_TOP_LEVEL = {"version", "project", "framework"}
ALLOWED_TOP_LEVEL = REQUIRED_TOP_LEVEL | OPTIONAL_TOP_LEVEL


def validate(data):
    errors = []
    warnings = []
    total_steps = 0
    seen_journey_ids = set()
    seen_step_ids = set()

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
        prefix = "journey[%d]" % ji

        if not isinstance(journey, dict):
            errors.append("%s: must be an object" % prefix)
            continue

        # Required journey fields
        for field in ("id", "name", "steps"):
            if field not in journey:
                errors.append("%s: missing required field \"%s\"" % (prefix, field))

        jid = journey.get("id")
        if jid is not None:
            if not isinstance(jid, str):
                errors.append("%s: \"id\" must be a string" % prefix)
            elif jid in seen_journey_ids:
                errors.append("%s: duplicate journey id \"%s\"" % (prefix, jid))
            else:
                seen_journey_ids.add(jid)

        if "name" in journey and not isinstance(journey["name"], str):
            errors.append("%s: \"name\" must be a string" % prefix)

        steps = journey.get("steps")
        if steps is not None:
            if not isinstance(steps, list):
                errors.append("%s: \"steps\" must be an array" % prefix)
                continue
            if len(steps) == 0:
                errors.append("%s: \"steps\" must not be empty" % prefix)
                continue

            for si, step in enumerate(steps):
                sp = "%s.steps[%d]" % (prefix, si)
                total_steps += 1

                if not isinstance(step, dict):
                    errors.append("%s: must be an object" % sp)
                    continue

                for field in ("id", "action", "screen"):
                    if field not in step:
                        errors.append("%s: missing required field \"%s\"" % (sp, field))

                sid = step.get("id")
                if sid is not None:
                    if not isinstance(sid, str):
                        errors.append("%s: \"id\" must be a string" % sp)
                    elif not STEP_ID_PATTERN.match(sid):
                        errors.append("%s: \"id\" must match PREFIX-NN pattern (got \"%s\")" % (sp, sid))
                    elif sid in seen_step_ids:
                        errors.append("%s: duplicate step id \"%s\"" % (sp, sid))
                    else:
                        seen_step_ids.add(sid)

                if "action" in step and not isinstance(step["action"], str):
                    errors.append("%s: \"action\" must be a string" % sp)

                if "screen" in step and not isinstance(step["screen"], str):
                    errors.append("%s: \"screen\" must be a string" % sp)

                if "tested" not in step:
                    errors.append("%s: missing required field \"tested\"" % sp)
                else:
                    tested = step["tested"]
                    if tested not in VALID_TESTED_VALUES:
                        errors.append("%s: \"tested\" must be true, false, or \"partial\" (got %s)" % (sp, json.dumps(tested)))
                    elif tested == "partial" and "note" not in step:
                        warnings.append("%s: tested is \"partial\" but no \"note\" field provided" % sp)

    return errors, warnings, total_steps


def main():
    parser = argparse.ArgumentParser(description="Validate a journeys.json file")
    parser.add_argument("path", help="Path to journeys.json")
    args = parser.parse_args()

    # Read and parse JSON
    try:
        with open(args.path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: File not found: %s" % args.path, file=sys.stderr)
        print(json.dumps({"valid": False, "errors": ["File not found: %s" % args.path], "warnings": [], "stats": {"journeys": 0, "steps": 0}}, indent=2))
        sys.exit(1)
    except json.JSONDecodeError as e:
        msg = "Invalid JSON: %s (line %d, col %d)" % (e.msg, e.lineno, e.colno)
        print("ERROR: %s" % msg, file=sys.stderr)
        print(json.dumps({"valid": False, "errors": [msg], "warnings": [], "stats": {"journeys": 0, "steps": 0}}, indent=2))
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
            print("ERROR: %s" % err, file=sys.stderr)
        sys.exit(1)

    if warnings:
        for w in warnings:
            print("WARNING: %s" % w, file=sys.stderr)


if __name__ == "__main__":
    main()
