---
name: scouting
description: "Writes failing tests for all planned checkpoints (RED phase of TDD) and captures failure evidence. Use after planning when task files exist. Do not use for writing implementation code or before planning is complete."
---

# Scouting

<HARD-GATE>
Requires `phases.plan.status === "approved"`. Do NOT write any implementation code. Tests ONLY.
</HARD-GATE>

## Process

For each checkpoint in dependency order:

1. **Write the test** (unit and/or e2e) using the runner from `state.json.testRunners`. See `docs/test-runners.md` for commands.
2. **Run the test — it must FAIL.** The failure must be because the feature doesn't exist, not because of typos or test bugs.
3. **Update the task file:**
```json
{
  "status": "red",
  "tests": { "unit": ["path/to/test.ts"] },
  "evidence": {
    "red": {
      "unit": "FAIL path/to/test.ts > description (expected undefined)",
      "timestamp": "<ISO-8601>"
    }
  }
}
```
4. **Commit:** `git add <test files> .pathfinder/tasks/<ID>.json && git commit -m "Scout: Mark trail for <ID>"`

After ALL checkpoints have failing tests:

5. **Validate:** Run `python3 scripts/verify-all-red.py .pathfinder/tasks`
6. **Run full suite** to confirm all new tests fail.
7. **Create scout gate** (`.pathfinder/scout.json`):
```json
{
  "status": "complete",
  "timestamp": "<ISO-8601>",
  "expedition": "<name>",
  "checkpointsScouted": "<N>",
  "allTestsFail": true
}
```
8. **Update state:** `currentPhase: "scout"`, `phases.scout.status: "complete"`, move all `planned` → `red` in counts.
9. **Commit:** `git add .pathfinder/ && git commit -m "Scout: All N checkpoints marked (RED)"`

## Error Handling

- If a test **passes** without implementation → test is wrong. It's testing existing behavior. Rewrite it.
- If a test fails for the **wrong reason** (import error, typo) → fix the test, document in `builderNotes`.
- Run `verify-all-red.py` before creating the scout gate.

## Output

- Test files for every checkpoint
- All tasks updated to `status: "red"` with failure evidence
- `.pathfinder/scout.json` — gate file
