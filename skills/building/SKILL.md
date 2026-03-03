---
name: building
description: "Implements minimal code to pass failing tests in dependency order (GREEN phase of TDD). Use after scouting when all checkpoints have failing tests. Do not use before scouting is complete or for writing new tests."
---

# Building

*Clear the trail one checkpoint at a time.*

## Overview

Building wraps `superpowers:subagent-driven-development` or `superpowers:executing-plans` (GREEN phase). You implement minimal code to pass each failing test, respecting dependency order. Task files enforce what can be worked on.

**Announce at start:** "I'm using the pathfinder:building skill to implement checkpoints."

## Prerequisites

- `.pathfinder/state.json` exists with `phases.scout.status === "complete"`
- All task files have `status: "red"` (tests written and failing)
- Scout gate exists: `.pathfinder/scout.json`

<HARD-GATE>
If scouting is not complete, REFUSE to build. Invoke pathfinder:scouting first.
Do NOT modify test files during building (unless fixing a genuine test bug, documented in builderNotes).
</HARD-GATE>

## The Process

### Step 1: Check Dependencies

Before working on ANY checkpoint:

```bash
bash scripts/pathfinder-check-deps.sh FEAT-01
```

If blocked, skip to the next unblocked checkpoint. Report which are blocked and why.

### Step 2: Build ONE Checkpoint at a Time

Read `testRunners` from `.pathfinder/state.json` to determine which commands to use. See `docs/test-runners.md` for the full command reference.

For each unblocked checkpoint, follow this strict loop:

1. **Read the task file** to understand what this checkpoint requires
2. **Run the failing test** to see the current error (using configured e2e + unit runners)
3. **Write minimal implementation code** to make the test pass
4. **Run the test again** to verify it passes
5. **Run the full suite** to check for regressions

### Step 3: Update Task File

After the checkpoint's tests pass:

```python
import json, datetime
task = json.load(open('.pathfinder/tasks/FEAT-01.json'))
task['status'] = 'green'
task['evidence']['green'] = {
    'e2e': 'PASS e2e/feature.spec.ts > FEAT-01 (1.2s)',
    'unit': 'PASS src/utils/feature.test.ts > FEAT-01 (3ms)',
    'fullSuite': 'Tests: N passed, 0 failed',
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}
task['builderNotes'] = '<brief note on implementation approach>'
json.dump(task, open('.pathfinder/tasks/FEAT-01.json', 'w'), indent=2)
```

### Step 4: Commit

```bash
git add src/ .pathfinder/tasks/FEAT-01.json
git commit -m "Builder: Clear FEAT-01"
```

### Step 5: Repeat for All Checkpoints

Continue in dependency order until all checkpoints are `green`.

### Step 6: Create Build Gate

After ALL checkpoints are green:

```bash
cat > .pathfinder/build.json << 'EOF'
{
  "status": "complete",
  "timestamp": "<ISO-8601>",
  "expedition": "<expedition-name>",
  "checkpointsCleared": <number>,
  "fullSuiteResult": "Tests: N passed, 0 failed"
}
EOF
```

### Step 7: Update State

```bash
bash scripts/pathfinder-update-state.sh
```

Then:

```python
import json
state = json.load(open('.pathfinder/state.json'))
state['currentPhase'] = 'build'
state['phases']['build'] = {'status': 'complete', 'timestamp': '<ISO-8601>'}
json.dump(state, open('.pathfinder/state.json', 'w'), indent=2)
```

### Step 8: Commit and Transition

```bash
git add .pathfinder/
git commit -m "Builder: All N checkpoints cleared (GREEN)"
```

Announce: "Build complete. All N checkpoints passing. Ready for reporting — invoke `pathfinder:reporting` or say `/report`."

## Subagent Dispatch (for large expeditions)

For expeditions with 5+ checkpoints, use `superpowers:subagent-driven-development`:

Dispatch one subagent per checkpoint with this template:

```
You are a BUILDER for checkpoint FEAT-01 in a Pathfinder expedition.

TASK: <checkpoint description>

TEST RUNNERS (from state.json):
- e2e: <e2e runner> (see docs/test-runners.md for commands)
- unit: <unit runner>

BEFORE YOU START:
1. Run: bash scripts/pathfinder-check-deps.sh FEAT-01
2. If blocked, report back immediately — do NOT proceed.

BUILD LOOP:
1. Run failing test using the configured runner
2. Write minimal code to pass it
3. Run test again — must PASS
4. Run full suite — must not regress
5. Update .pathfinder/tasks/FEAT-01.json (status→green, evidence)
6. Commit: "Builder: Clear FEAT-01"

Do NOT modify test files. Do NOT work on other checkpoints.
```

After each subagent completes, review with `superpowers:requesting-code-review`.

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| Building checkpoints out of dependency order | Always check deps first |
| Writing more code than needed to pass tests | Minimal implementation only |
| Modifying tests to make them pass | Fix implementation, not tests |
| Skipping the full suite check | Regressions compound — catch them early |
| Claiming "tests pass" without running them | Capture actual test output as evidence |
| Working on multiple checkpoints simultaneously | One at a time, commit each |

## Error Handling
* If `scripts/pathfinder-check-deps.sh` reports blocked dependencies, skip the checkpoint and move to the next unblocked one.
* If a test fails after implementation, do NOT modify the test. Debug the implementation using `superpowers:systematic-debugging`.
* If the full suite regresses, revert the last change and investigate before proceeding.

## Output

- Implementation code for all checkpoints
- `.pathfinder/tasks/FEAT-XX.json` — all updated to `status: "green"` with evidence
- `.pathfinder/build.json` — gate file
- Updated `.pathfinder/state.json`
