# UI Testing

Generate framework-correct UI tests with proper selectors, waits, and assertions for any stack.

## Process

1. **Detect framework:** Run `python3 scripts/detect-ui-framework.py .` to identify the project's UI test stack.
2. **Read framework reference:** Based on detected framework, read the matching file from `references/`:
   - Web: `references/playwright.md` or `references/cypress.md`
   - React Native: `references/maestro.md` or `references/detox.md`
   - iOS: `references/xcuitest.md`
   - Android: `references/espresso.md`
   - Flutter: `references/flutter-test.md`
3. **Generate test skeleton:** Run `python3 scripts/generate-ui-test.py` with checkpoint details.
4. **Run the test** to verify it works.
5. **Capture screenshot evidence** when available.

## Selector Strategy (universal)

Prefer accessibility-based selectors over implementation details:

| Priority | Selector Type | Example |
|----------|--------------|---------|
| 1st | Test ID | `data-testid`, `testID`, `accessibilityLabel` |
| 2nd | Role + name | `getByRole('button', { name: 'Submit' })` |
| 3rd | Text content | `getByText('Save')`, `text: "Save"` |
| 4th | CSS/XPath | Last resort only |

## Wait Strategy (universal)

Avoid `sleep()` and unreliable `networkidle` -- prefer condition-based waits:

| Condition | Why |
|-----------|-----|
| Element visible/exists | UI rendered |
| Specific element appears | Data loaded (more reliable than network idle) |
| Animation complete | Transitions done |
| Text appears/disappears | State changed |
| `domcontentloaded` | Page structure ready (Playwright) |

## Visual Regression

When the framework supports screenshots:

1. Capture baseline: `python3 scripts/snapshot-compare.py capture <name>`
2. Compare after changes: `python3 scripts/snapshot-compare.py compare <name>`
3. Evidence stored in `<testDir>/pathfinder/baselines/`

## Error Handling

- Framework not detected → ask user to specify, update `<testDir>/pathfinder/config.json`
- Test passes without implementation → test is wrong, targets existing behavior
- Flaky test → check for missing waits, add condition-based waiting
- Screenshot diff > 5% → review visual change, update baseline if intentional
