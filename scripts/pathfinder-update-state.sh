#!/usr/bin/env bash
# Pathfinder v0.4.0 — State Updater
# Updates state.json checkpoint counts from task files.
set -euo pipefail

if ! command -v python3 &>/dev/null; then
  echo "✘ python3 is required but not found in PATH"
  exit 1
fi

if [ ! -f .pathfinder/state.json ]; then
  echo "✘ No .pathfinder/state.json found"
  exit 1
fi

python3 -c "
import json, glob, sys, os, tempfile

ALLOWED_STATUSES = {'planned', 'red', 'green', 'verified'}

state = json.load(open('.pathfinder/state.json'))
counts = {'total': 0, 'planned': 0, 'red': 0, 'green': 0, 'verified': 0}

for f in sorted(glob.glob('.pathfinder/tasks/*.json')):
    t = json.load(open(f))
    status = t.get('status', 'planned')
    if status not in ALLOWED_STATUSES:
        print(f'⚠ Unknown status \"{status}\" in {f}, treating as planned')
        status = 'planned'
    counts['total'] += 1
    counts[status] = counts.get(status, 0) + 1

state['checkpoints'] = counts

# Atomic write: temp file then rename
fd, tmp_path = tempfile.mkstemp(dir='.pathfinder', suffix='.tmp')
try:
    with os.fdopen(fd, 'w') as tmp:
        json.dump(state, tmp, indent=2)
    os.rename(tmp_path, '.pathfinder/state.json')
except:
    os.unlink(tmp_path)
    raise

print(f'State updated: {counts}')
"
