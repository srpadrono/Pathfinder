# Summiting

Run all tests, update the journey map, regenerate diagrams with before/after comparison, and report coverage.

## Process

1. **Save baseline (if starting fresh):** If no baseline exists yet, one is auto-created on diagram generation. To explicitly reset the baseline before a test run:
```bash
python3 scripts/generate-diagrams.py <testDir>/pathfinder/journeys.json --save-baseline
```

2. **Run the full UI test suite** using the detected framework. Read the matching framework reference in `references/` for commands.
```bash
python3 scripts/detect-ui-framework.py .
# Then run the appropriate command (e.g., tuist test, xcodebuild test, npx playwright test)
```

3. **For each test result**, update `<testDir>/pathfinder/journeys.json`:
   - Test passes → `"tested": true`
   - Test fails → `"tested": false` (regression or incomplete implementation)
   - Test disabled with comment → `"tested": "partial"` with `"note"` explaining why
   - See references/scouting.md for test marking conventions.

4. **Regenerate diagrams:**
```bash
python3 scripts/generate-diagrams.py <testDir>/pathfinder/journeys.json
```
This produces:
   - **Legend** — symbol/colour reference
   - **📸 Before (Baseline)** — decision tree at baseline coverage
   - **🚀 After (Current)** — decision tree with current coverage
   - **📊 Coverage Delta** — table showing steps gained/lost per journey
   - **Per-journey flowcharts** — detailed view of each journey
   - **Summary table** — overall coverage percentage

5. **Compute coverage score:**
```bash
python3 scripts/coverage-score.py <testDir>/pathfinder/journeys.json
```

6. **Commit:**
```bash
git add <testDir>/pathfinder/
git commit -m "Verify: Coverage at X% (Y/Z steps tested)"
```

7. **If creating a PR**, include the diagrams and coverage delta from `<testDir>/pathfinder/blazes.md` in the PR body. The before/after comparison shows reviewers exactly what improved.

## Coverage Thresholds

| Coverage | Status | Action |
|----------|--------|--------|
| 🟢 80%+ | Excellent | Merge-ready |
| 🟡 50-79% | Acceptable | Document gaps, mark partial steps with notes |
| 🔴 <50% | Insufficient | Continue scouting |

## After Completion

When a coverage sprint is done, reset the baseline for the next round:
```bash
python3 scripts/generate-diagrams.py <testDir>/pathfinder/journeys.json --save-baseline
```

This makes the current coverage the new "before" for future comparison.

## Error Handling

- Tests fail that previously passed → regression. Fix before proceeding.
- Coverage drops after code changes → new untested journeys. Re-run `/map`.
- Framework not available (no simulator/emulator) → mark steps as `tested: "partial"`, note the limitation.
- Disabled tests → keep them in the codebase with clear comments; mark as `"partial"` in journeys.json so the decision tree shows ⚠️ amber instead of ❌ red.
