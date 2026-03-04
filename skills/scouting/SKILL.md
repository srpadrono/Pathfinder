---
name: scouting
description: "Writes UI tests for untested journey steps (❌ → ✅) using the detected framework. Use after diagramming when coverage gaps are identified. Do not use before mapping and diagramming are complete."
---

# Scouting

Write UI tests for every ❌ step in the journey map. Each test you write flips a step from ❌ to ✅.

## Process

1. **Read the journey map:** `.pathfinder/journeys.json`
2. **Read the diagram:** `.pathfinder/diagrams.md` — identify all ❌ steps.
3. **Prioritize:** Test the most critical journeys first (auth, core CRUD, then secondary flows).

For each untested step:

4. **Generate test skeleton:**
```bash
python3 skills/ui-testing/scripts/generate-ui-test.py <STEP-ID> "<action>" <framework> --route <screen>
```
5. **Read framework reference:** `skills/ui-testing/references/<framework>.md` for correct selectors and waits.
6. **Fill in the test** with real selectors, actions, and assertions for that step.
7. **Run the test.** It should FAIL (the step isn't implemented or the test captures current behavior).
8. **Update journey map** — set `tested: true` and add `testFile`:
```python
import json
data = json.load(open('.pathfinder/journeys.json'))
# Find step, set tested=True, testFile="e2e/auth_01.spec.ts"
json.dump(data, open('.pathfinder/journeys.json', 'w'), indent=2)
```
9. **Commit per journey:**
```bash
git add <test files> .pathfinder/journeys.json
git commit -m "Scout: Test AUTH journey (5 steps)"
```

After testing a batch of steps:

10. **Regenerate diagrams:**
```bash
python3 skills/diagramming/scripts/generate-diagrams.py .pathfinder/journeys.json
```
11. **Commit updated diagram:** `git add .pathfinder/diagrams.md && git commit -m "Diagram: Coverage now X%"`

## Error Handling

- Test **passes** on existing code → great, the feature works. Still mark as `tested: true`.
- Framework not installed → run `python3 skills/ui-testing/scripts/detect-ui-framework.py .` and install.
- Step is untestable (e.g., native OS dialog) → mark as `tested: "partial"` with a note.
