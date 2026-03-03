---
name: scouting
description: "Writes failing UI and unit tests for all planned checkpoints (RED phase of TDD) and captures failure evidence. Use after planning when task files exist. Do not use for writing implementation code or before planning is complete."
---

# Scouting

<HARD-GATE>
Requires `phases.plan.status === "approved"`. Do NOT write any implementation code. Tests ONLY.
</HARD-GATE>

## Process

For each checkpoint in dependency order:

1. **Generate UI test skeleton:** Run `python3 skills/ui-testing/scripts/generate-ui-test.py <ID> "<description>" <framework>` — then fill in selectors and assertions. Read the matching `skills/ui-testing/references/<framework>.md` for correct patterns.
2. **Write the unit test** using the runner from `state.json.testRunners.unit`.
3. **Run both tests — they must FAIL.** Failure must be because the feature doesn't exist, not test bugs.
4. **Update the task file:**
```json
{
  "status": "red",
  "tests": { "e2e": ["e2e/feat_01.spec.ts"], "unit": ["src/feat.test.ts"] },
  "evidence": {
    "red": {
      "e2e": "FAIL e2e/feat_01.spec.ts > FEAT-01 (timeout)",
      "unit": "FAIL src/feat.test.ts > FEAT-01 (expected undefined)",
      "timestamp": "<ISO-8601>"
    }
  }
}
```
5. **Commit:** `git add <test files> .pathfinder/tasks/<ID>.json && git commit -m "Scout: Mark trail for <ID>"`

After ALL checkpoints have failing tests:

6. **Validate:** Run `python3 scripts/verify-all-red.py .pathfinder/tasks`
7. **Create scout gate** (`.pathfinder/scout.json`)
8. **Update state:** `currentPhase: "scout"`, `phases.scout.status: "complete"`
9. **Commit:** `git add .pathfinder/ && git commit -m "Scout: All N checkpoints marked (RED)"`

## Error Handling

- Test **passes** without implementation → test is wrong. Rewrite it.
- Test fails for **wrong reason** (import error, typo) → fix the test, document in `builderNotes`.
- No UI test framework installed → run `python3 skills/ui-testing/scripts/detect-ui-framework.py .` and install the suggested framework.
