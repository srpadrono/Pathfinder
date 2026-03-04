---
name: summiting
description: "Runs all UI tests, updates the journey diagram with results, and computes coverage score. Use after scouting to validate test coverage. Do not use before any tests have been written."
---

# Summiting

Run all tests, update the journey map, regenerate the diagram, and report coverage.

## Process

1. **Run the full UI test suite** using the detected framework. Read the matching framework reference in `skills/ui-testing/references/` for commands.
```bash
python3 skills/ui-testing/scripts/detect-ui-framework.py .
# Then run the appropriate command
```

2. **For each test result**, update `.pathfinder/journeys.json`:
   - Test passes → `tested: true`
   - Test fails → `tested: false` (regression or incomplete implementation)

3. **Regenerate diagrams:**
```bash
python3 skills/blazing/scripts/generate-diagrams.py .pathfinder/journeys.json
```

4. **Compute coverage score:**
```bash
python3 scripts/coverage-score.py .pathfinder/journeys.json
```

5. **Commit:**
```bash
git add .pathfinder/
git commit -m "Verify: Coverage at X% (Y/Z steps tested)"
```

6. **If creating a PR**, include the diagrams and coverage summary from `.pathfinder/blazes.md` in the PR body.

## Coverage Thresholds

| Coverage | Status | Action |
|----------|--------|--------|
| 🟢 80%+ | Excellent | Merge-ready |
| 🟡 50-79% | Acceptable | Document gaps |
| 🔴 <50% | Insufficient | Continue scouting |

## Error Handling

- Tests fail that previously passed → regression. Fix before proceeding.
- Coverage drops after code changes → new untested journeys. Re-run `/map`.
- Framework not available (no simulator/emulator) → mark steps as `tested: "partial"`, note the limitation.
