---
name: scouting
description: "Writes UI tests for untested journey steps, verifying existing behavior or catching missing functionality. Use after diagramming when coverage gaps are identified. Do not use before mapping and diagramming are complete."
---

# Scouting

Write UI tests for every ❌ step in the journey map. Each test verifies that a user journey step works correctly.

## Process

1. **Read the journey map:** `.pathfinder/journeys.json`
2. **Read the diagram:** `.pathfinder/diagrams.md` — identify all ❌ steps.
3. **Prioritize:** Critical journeys first (auth, core CRUD), then secondary flows.

For each untested step:

4. **Generate test:** `python3 skills/ui-testing/scripts/generate-ui-test.py <STEP-ID> "<action>" <framework> --route <screen> --auto`
   - `--auto` appends to existing journey file if found, creates new file if not.
5. **Read framework reference:** `skills/ui-testing/references/<framework>.md` for correct selectors and waits.
6. **Fill in the test** with real selectors, actions, and assertions matching the actual UI.
7. **Run the test.**
   - **Passes** → the feature works, step is now covered. Mark `tested: true`.
   - **Fails** → either the test needs fixing (wrong selector) or a real bug was found. Investigate before marking.
8. **Update `journeys.json`:** Set `tested: true` and add `testFile` for the step.
9. **Commit per journey:**
```bash
git add <test files> .pathfinder/journeys.json
git commit -m "Scout: Test <JOURNEY> journey (N steps)"
```

After testing a batch:

10. **Regenerate diagrams:** `python3 skills/diagramming/scripts/generate-diagrams.py .pathfinder/journeys.json`
11. **Commit:** `git add .pathfinder/diagrams.md && git commit -m "Diagram: Coverage now X%"`

## Error Handling

- Framework not installed → run `python3 skills/ui-testing/scripts/detect-ui-framework.py .` and install.
- Test fails due to wrong selector → read the component source, fix the selector.
- Step is untestable (native OS dialog, third-party auth redirect) → mark `tested: "partial"` with a note.
