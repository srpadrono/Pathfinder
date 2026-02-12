#!/usr/bin/env bash
# Pathfinder v0.4.0 — State Updater
# Updates state.json checkpoint counts from task files.
set -euo pipefail

if [ ! -f .pathfinder/state.json ]; then
  echo "✘ No .pathfinder/state.json found"
  exit 1
fi

python3 -c "
import json, glob

state = json.load(open('.pathfinder/state.json'))
counts = {'total': 0, 'planned': 0, 'red': 0, 'green': 0, 'verified': 0}

for f in sorted(glob.glob('.pathfinder/tasks/*.json')):
    t = json.load(open(f))
    status = t.get('status', 'planned')
    counts['total'] += 1
    counts[status] = counts.get(status, 0) + 1

state['checkpoints'] = counts
json.dump(state, open('.pathfinder/state.json', 'w'), indent=2)
print(f'State updated: {counts}')
"
