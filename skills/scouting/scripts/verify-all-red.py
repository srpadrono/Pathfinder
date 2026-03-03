#!/usr/bin/env python3
"""Verify all task files are in 'red' status with evidence. Stdout report."""
import json, glob, sys, os

tasks_dir = sys.argv[1] if len(sys.argv) > 1 else ".pathfinder/tasks"
errors = []
total = 0

for f in sorted(glob.glob(os.path.join(tasks_dir, "*.json"))):
    t = json.load(open(f))
    tid = t.get("id", os.path.basename(f))
    total += 1

    if t.get("status") != "red":
        errors.append(f"NOT RED: {tid} has status '{t.get('status')}'")

    if not t.get("evidence", {}).get("red"):
        errors.append(f"NO EVIDENCE: {tid} missing red evidence")

    if not t.get("tests", {}).get("unit") and not t.get("tests", {}).get("e2e"):
        errors.append(f"NO TESTS: {tid} has no test files listed")

if errors:
    for e in errors:
        print(e, file=sys.stderr)
    print(f"FAIL: {len(errors)} issues in {total} tasks")
    sys.exit(1)
else:
    print(f"SUCCESS: All {total} tasks are RED with evidence")
    sys.exit(0)
