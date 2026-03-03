---
name: building
description: "Implements minimal code to pass failing tests in dependency order (GREEN phase of TDD). Use after scouting when all checkpoints have failing tests. Do not use before scouting is complete or for writing new tests."
---

# Building

<HARD-GATE>
Requires `phases.scout.status === "complete"`. Do NOT modify test files (unless fixing a genuine test bug — document in builderNotes).
</HARD-GATE>

## Process

For each checkpoint in dependency order:

1. **Check dependencies:** `bash scripts/pathfinder-check-deps.sh <ID>` — if blocked, skip to next.
2. **Run the failing test** to see the current error.
3. **Write minimal code** to make it pass. Nothing more.
4. **Run the test again** — must PASS.
5. **Run the full suite** — no regressions.
6. **Update task file:**
```json
{
  "status": "green",
  "evidence": {
    "green": {
      "unit": "PASS path/to/test.ts > description (3ms)",
      "fullSuite": "Tests: N passed, 0 failed",
      "timestamp": "<ISO-8601>"
    }
  },
  "builderNotes": "brief implementation note"
}
```
7. **Commit:** `git add src/ .pathfinder/tasks/<ID>.json && git commit -m "Builder: Clear <ID>"`

After ALL checkpoints are green:

8. **Create build gate** (`.pathfinder/build.json`):
```json
{
  "status": "complete",
  "timestamp": "<ISO-8601>",
  "expedition": "<name>",
  "checkpointsCleared": "<N>",
  "fullSuiteResult": "Tests: N passed, 0 failed"
}
```
9. **Update state:** `currentPhase: "build"`, `phases.build.status: "complete"`.
10. **Commit:** `git add .pathfinder/ && git commit -m "Builder: All N checkpoints cleared (GREEN)"`

## Subagent Dispatch (5+ checkpoints)

Dispatch one agent per checkpoint:
```
You are a BUILDER for checkpoint <ID>.
TASK: <description>
1. Run: bash scripts/pathfinder-check-deps.sh <ID> — if blocked, stop.
2. Run failing test → write minimal code → run test (must PASS) → run full suite (no regressions)
3. Update .pathfinder/tasks/<ID>.json (status→green, evidence)
4. Commit: "Builder: Clear <ID>"
Do NOT modify tests. Do NOT touch other checkpoints.
```

## Error Handling

- If deps are blocked, skip and move to the next unblocked checkpoint.
- If a test fails after implementation, do NOT modify the test. Debug the implementation.
- If the full suite regresses, revert and investigate before proceeding.

## Output

- Implementation code for all checkpoints
- All tasks updated to `status: "green"` with evidence
- `.pathfinder/build.json` — gate file
