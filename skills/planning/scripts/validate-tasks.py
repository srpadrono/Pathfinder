#!/usr/bin/env python3
"""Validate task files: check for cycles, missing deps, valid fields. Outputs report to stdout."""
import json, glob, sys, os

tasks_dir = sys.argv[1] if len(sys.argv) > 1 else ".pathfinder/tasks"
errors = []
tasks = {}

for f in sorted(glob.glob(os.path.join(tasks_dir, "*.json"))):
    try:
        t = json.load(open(f))
    except json.JSONDecodeError as e:
        errors.append(f"PARSE ERROR: {f}: {e}")
        continue

    tid = t.get("id", os.path.basename(f))
    tasks[tid] = t

    # Required fields
    for field in ["id", "description", "category", "priority", "status", "dependencies"]:
        if field not in t:
            errors.append(f"MISSING FIELD: {tid} missing '{field}'")

    # Valid status
    if t.get("status") not in ["planned", "red", "green", "verified"]:
        errors.append(f"INVALID STATUS: {tid} has status '{t.get('status')}'")

    # Valid priority
    if t.get("priority") not in ["must", "should", "could"]:
        errors.append(f"INVALID PRIORITY: {tid} has priority '{t.get('priority')}'")

# Check deps exist
for tid, t in tasks.items():
    for dep in t.get("dependencies", []):
        if dep not in tasks:
            errors.append(f"MISSING DEP: {tid} depends on {dep} which doesn't exist")

# Check for cycles (simple DFS)
def has_cycle(node, visited, stack):
    visited.add(node)
    stack.add(node)
    for dep in tasks.get(node, {}).get("dependencies", []):
        if dep in stack:
            return True
        if dep not in visited and has_cycle(dep, visited, stack):
            return True
    stack.discard(node)
    return False

visited, stack = set(), set()
for tid in tasks:
    if tid not in visited:
        if has_cycle(tid, visited, stack):
            errors.append(f"CYCLE DETECTED involving {tid}")

if errors:
    for e in errors:
        print(e, file=sys.stderr)
    print(f"FAIL: {len(errors)} validation errors in {len(tasks)} tasks")
    sys.exit(1)
else:
    print(f"SUCCESS: {len(tasks)} tasks validated, no errors")
    sys.exit(0)
