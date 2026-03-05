---
name: scout
description: "Writes UI tests for untested steps in the journey map using framework-correct selectors, waits, and patterns. Use when the user says /scout or wants to write tests for coverage gaps."
---

# Scouting

Write UI tests for every untested step in the journey map. Each test verifies that a user journey step works correctly.

## Process

1. **Read the journey map:** `<testDir>/pathfinder/journeys.json`
2. **Read the diagram:** `<testDir>/pathfinder/blazes.md` — identify all untested steps. The decision tree makes gaps easy to spot.
3. **Prioritize:** Critical journeys first (auth, core CRUD), then secondary flows, then error paths.

For each untested step:

4. **Read existing test patterns** in the project. Match the style, naming conventions, and test architecture already in use (e.g., BDD protocols, page objects, test fixtures).
5. **Read framework reference:** Load the matching framework reference from the pathfinder skill for correct selectors, waits, and patterns.
6. **Generate test:**
```bash
python3 "${CLAUDE_SKILL_DIR}/../pathfinder/scripts/generate-ui-test.py" <STEP-ID> "<action>" <framework> --route <screen> --auto
```
   - `--auto` appends to existing journey file if found, creates new file if not.
7. **Fill in the test** with real selectors, actions, and assertions matching the actual UI.
   - Use localized strings from the project's resources (e.g., `Localizable.strings`) for button labels.
   - Match the existing test hierarchy/protocol patterns.
8. **Run the test.**
   - **Passes** → the feature works, step is now covered. Mark `tested: true`.
   - **Fails** → either the test needs fixing (wrong selector) or a real bug was found. Investigate before marking.
9. **Update `journeys.json`:** Set `tested: true` and add `testFile` for the step.
10. **Commit per journey:**
```bash
git add <test files> <testDir>/pathfinder/journeys.json
git commit -m "Scout: Test <JOURNEY> journey (N steps)"
```

### Handling untestable steps

Some steps can't pass in the current test environment (e.g., mock API always succeeds, no error injection):
- Write the test anyway so it's ready when the test infrastructure supports it
- Disable the test with a clear comment explaining the blocker
- Mark the step as `"tested": "partial"` with a `"note"` field:
```json
{ "id": "ERROR-01", "tested": "partial", "note": "test disabled — mock API always succeeds, needs failure injection" }
```

After testing a batch:

11. **Regenerate diagrams:**
```bash
python3 "${CLAUDE_SKILL_DIR}/../pathfinder/scripts/generate-diagrams.py" <testDir>/pathfinder/journeys.json
```
    - The before/after comparison will show your progress since the baseline
12. **Commit:** `git add <testDir>/pathfinder/blazes.md && git commit -m "Diagram: Coverage now X%"`

## Error Handling

- Framework not installed → run `python3 "${CLAUDE_SKILL_DIR}/../pathfinder/scripts/detect-ui-framework.py" .` and install.
- Test fails due to wrong selector → read the component source and localized strings, fix the selector.
- Step is untestable (native OS dialog, third-party auth redirect) → mark `tested: "partial"` with a note.
