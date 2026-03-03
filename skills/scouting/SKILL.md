---
name: scouting
description: "Writes failing tests for all planned checkpoints (RED phase of TDD) and captures failure evidence. Use after planning when task files exist. Do not use for writing implementation code or before planning is complete."
---

# Scouting

*Mark the trail with failing tests before anyone builds.*

## Overview

Scouting wraps `superpowers:test-driven-development` (RED phase only). You write failing tests for every planned checkpoint and capture the failure evidence in task files. No implementation code is written during scouting.

**Announce at start:** "I'm using the pathfinder:scouting skill to write failing tests for all checkpoints."

## Prerequisites

- `.pathfinder/state.json` exists with `phases.plan.status === "approved"`
- Task files exist in `.pathfinder/tasks/`
- All tasks have `status: "planned"`

<HARD-GATE>
If plan is not approved, REFUSE to scout. Invoke pathfinder:planning first.
Do NOT write any implementation code during scouting. Tests ONLY.
</HARD-GATE>

## The Process

### Step 1: Read All Task Files

```bash
for f in .pathfinder/tasks/*.json; do
  echo "=== $(basename $f) ==="
  cat "$f"
done
```

### Step 2: For Each Checkpoint (in dependency order)

Read `testRunners` from `.pathfinder/state.json` to determine which commands to use. See `docs/test-runners.md` for the full command reference.

Follow `superpowers:test-driven-development` RED phase:

1. **Write the e2e test** — using the configured e2e runner (Playwright, Maestro, Cypress, etc.)
2. **Write the unit test** — using the configured unit runner (Vitest, Jest, pytest, etc.)
3. **Run tests to verify they FAIL** using the appropriate runner commands
4. **Verify the failure is correct** — should fail because feature doesn't exist, NOT because of typos or test bugs

### Step 3: Capture Evidence in Task File

After confirming tests fail correctly:

```python
import json
task = json.load(open('.pathfinder/tasks/FEAT-01.json'))
task['status'] = 'red'
task['tests'] = {
    'e2e': ['e2e/feature.spec.ts'],
    'unit': ['src/utils/feature.test.ts']
}
task['evidence']['red'] = {
    'e2e': 'FAIL e2e/feature.spec.ts > FEAT-01 (timeout waiting for locator)',
    'unit': 'FAIL src/utils/feature.test.ts > FEAT-01 (expected undefined)',
    'timestamp': '<ISO-8601>'
}
json.dump(task, open('.pathfinder/tasks/FEAT-01.json', 'w'), indent=2)
```

### Step 4: Commit After Each Checkpoint's Tests

```bash
git add e2e/ src/**/*.test.* .pathfinder/tasks/FEAT-01.json
git commit -m "Scout: Mark trail for FEAT-01"
```

### Step 4b: Validate All Red

Execute: `python3 scripts/verify-all-red.py .pathfinder/tasks` to confirm all tasks are RED with evidence.

### Step 5: Create Scout Gate

After ALL checkpoints have tests:

```bash
cat > .pathfinder/scout.json << 'EOF'
{
  "status": "complete",
  "timestamp": "<ISO-8601>",
  "expedition": "<expedition-name>",
  "checkpointsScounted": <number>,
  "allTestsFail": true
}
EOF
```

### Step 6: Update State

```python
import json
state = json.load(open('.pathfinder/state.json'))
state['currentPhase'] = 'scout'
state['phases']['scout'] = {'status': 'complete', 'timestamp': '<ISO-8601>'}
state['checkpoints']['planned'] = 0
state['checkpoints']['red'] = state['checkpoints']['total']
json.dump(state, open('.pathfinder/state.json', 'w'), indent=2)
```

### Step 7: Final Verification

Run ALL tests together to confirm they all fail using the configured runners (e.g. `npx playwright test`, `maestro test e2e/flows/`, `npx vitest run`, `npx jest`, etc.).

Commit the scout gate:

```bash
git add .pathfinder/scout.json .pathfinder/state.json
git commit -m "Scout: All N checkpoints marked (RED)"
```

### Step 8: Transition to Building

Announce: "Scouting complete. N checkpoints marked with failing tests. Ready for building — invoke `pathfinder:building` or say `/build`."

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| Writing implementation code during scouting | Tests only — implementation comes in build phase |
| Tests that pass without implementation | Tests must FAIL — they test features that don't exist yet |
| Skipping unit tests, only writing e2e | Both e2e AND unit tests for each checkpoint |
| Not running tests to verify failure | Always run and capture the failure output |
| Writing all tests then committing once | Commit after each checkpoint's tests |

## Error Handling
* If a test passes without implementation, the test is wrong — it's testing existing behavior, not new functionality. Rewrite it.
* If a test fails for the wrong reason (import error, typo), fix the test and re-run. Document the fix in `builderNotes`.
* Run `python3 scripts/verify-all-red.py .pathfinder/tasks` before creating the scout gate to catch missing evidence.

## Output

- Test files for every checkpoint (e2e + unit)
- `.pathfinder/tasks/FEAT-XX.json` — all updated to `status: "red"` with failure evidence
- `.pathfinder/scout.json` — gate file
- Updated `.pathfinder/state.json`
