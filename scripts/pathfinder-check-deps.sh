#!/usr/bin/env bash
# Pathfinder v0.4.0 — Dependency Checker
# Usage: pathfinder-check-deps.sh <TASK-ID>
set -euo pipefail

TASK_ID="${1:?Usage: pathfinder-check-deps.sh <TASK-ID>}"
TASK_FILE=".pathfinder/tasks/${TASK_ID}.json"

if [ ! -f "$TASK_FILE" ]; then
  echo "✘ Task file not found: $TASK_FILE"
  exit 1
fi

python3 -c "
import json, sys

task = json.load(open('$TASK_FILE'))
deps = task.get('dependencies', [])

if not deps:
    print(f'✓ {task[\"id\"]} has no dependencies — unblocked')
    sys.exit(0)

blocked = False
for dep in deps:
    dep_file = f'.pathfinder/tasks/{dep}.json'
    try:
        dep_task = json.load(open(dep_file))
        if dep_task['status'] not in ('green', 'verified'):
            print(f'✘ Blocked: {task[\"id\"]} depends on {dep} (status: {dep_task[\"status\"]})')
            blocked = True
        else:
            print(f'  ✓ Dependency {dep} satisfied (status: {dep_task[\"status\"]})')
    except FileNotFoundError:
        print(f'✘ Dependency task file missing: {dep_file}')
        blocked = True

if blocked:
    sys.exit(1)

print(f'✓ {task[\"id\"]} is unblocked — all dependencies satisfied')
"
