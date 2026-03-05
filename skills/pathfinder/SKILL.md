---
name: pathfinder
description: "Discovers user journeys in any codebase, visualizes UI/E2E test coverage with Mermaid flowcharts showing tested and untested steps, and generates framework-correct tests to fill gaps. Triggers on test coverage analysis, journey mapping, UI testing gaps, coverage visualization, or E2E test generation for Playwright, Cypress, Maestro, Detox, XCUITest, Espresso, or Flutter projects. Not for unit tests, API tests, or backend-only projects."
---

# Pathfinder

Map every user journey. See what's tested. Fill the gaps. Track progress.

## Quick Start

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/pathfinder-init.py"
```

This auto-detects your test directory and creates `pathfinder/` inside it (e.g., `e2e/tests/pathfinder/`).
For monorepos, run init in each module. Use `${CLAUDE_SKILL_DIR}/scripts/aggregate.py` for a combined view.

## Workflow

```
/map -> /blaze -> /scout -> /summit
```

| Command | Phase | What happens |
|---------|-------|-------------|
| `/map` | Map | Crawl code, discover all user journeys, create journeys.json |
| `/blaze` | Blaze | Generate Mermaid flowcharts, decision tree, and coverage delta |
| `/scout` | Scout | Write UI tests for untested steps |
| `/summit` | Summit | Run tests, compare before/after, finalize coverage |

Each command is a skill — invoke it directly or let Claude chain them as needed.

### Partial Workflows

Not every situation needs the full cycle. Use what fits:

| User wants | Commands to run |
|------------|----------------|
| "What's our test coverage?" | `/map` then `/blaze` (discover + visualize) |
| "Write tests for the gaps" | `/scout` (assumes journeys.json exists) |
| "Update the coverage diagrams" | `/blaze` (regenerate from existing journeys.json) |
| "Full coverage sprint" | `/map` -> `/blaze` -> `/scout` -> `/summit` |
| "Show progress since last sprint" | `/blaze` (auto-compares with baseline) |

If `journeys.json` doesn't exist yet, always start with `/map`.

## Diagram Features

### Per-Journey Flowcharts
Each journey gets its own Mermaid flowchart with colour-coded nodes:
- Green **Tested** -- step has a passing UI test
- Amber **Partial** -- test written but disabled or implicitly covered
- Red **Untested** -- no UI test coverage

### Combined Decision Tree
All journeys merged into a single flowchart showing every branching path:
- Diamond nodes at decision points (e.g., user taps Confirm vs Decline)
- Dashed error arrows branching from API/loading steps
- Shared prefixes are merged so you can spot gaps at a glance

### Before/After Comparison
When a baseline exists, diagrams show:
- **Before (Baseline)** -- decision tree at the time coverage work started
- **After (Current)** -- decision tree with current coverage
- **Coverage Delta** -- table showing per-journey step changes

### Legend
A legend table is included at the top of every generated `blazes.md` explaining all symbols, colours, and arrow types.

## UI Test Generation

Read [references/ui-testing.md](references/ui-testing.md) for selector strategies, wait patterns, and visual regression.

Framework-specific patterns (only load the one matching the project):
- [references/playwright.md](references/playwright.md)
- [references/cypress.md](references/cypress.md)
- [references/maestro.md](references/maestro.md)
- [references/detox.md](references/detox.md)
- [references/xcuitest.md](references/xcuitest.md)
- [references/espresso.md](references/espresso.md)
- [references/flutter-test.md](references/flutter-test.md)

## Scripts

All scripts are Python 3 CLIs in the `scripts/` directory of this skill. They output JSON to stdout, errors to stderr. Reference them via `${CLAUDE_SKILL_DIR}/scripts/`.

| Script | Purpose |
|--------|---------|
| `scripts/pathfinder-init.py` | Initialize Pathfinder in a project |
| `scripts/scan-test-coverage.py .` | Scan existing tests and map to routes/screens |
| `scripts/detect-ui-framework.py .` | Auto-detect UI test framework |
| `scripts/generate-ui-test.py ID "desc" framework --auto` | Generate or append a UI test |
| `scripts/generate-diagrams.py journeys.json` | Generate flowcharts, decision tree, and delta |
| `scripts/generate-diagrams.py journeys.json --save-baseline` | Reset baseline to current state |
| `scripts/generate-diagrams.py journeys.json --clear-baseline` | Remove baseline (next run creates fresh one) |
| `scripts/coverage-score.py <testDir>/pathfinder/journeys.json` | Compute coverage percentage |
| `scripts/snapshot-compare.py capture\|compare name image` | Visual regression |
| `scripts/aggregate.py [root]` | Discover all modules, merge coverage summary |
| `scripts/validate-journeys.py <path>` | Validate journeys.json structure and fields |

## Project Files

| File | Purpose |
|------|---------|
| `<testDir>/pathfinder/config.json` | Project config (framework, test directory, auth) |
| `<testDir>/pathfinder/journeys.json` | Journey map -- source of truth |
| `<testDir>/pathfinder/journeys-baseline.json` | Baseline snapshot for before/after comparison (auto-created) |
| `<testDir>/pathfinder/blazes.md` | Mermaid coverage diagrams (auto-generated) |
| `assets/journeys-template.json` | Starter template for journeys.json |

## Configuration

Optional `<testDir>/pathfinder/config.json`:

```json
{
  "project": "my-app",
  "framework": "playwright",
  "testDir": "e2e/tests",
  "auth": { "storageState": "e2e/.auth/user.json" }
}
```

If absent, Pathfinder auto-detects from framework config files.

## Platform Notes

Pathfinder works across web, mobile, and desktop. The terminology adapts:

| Concept | Web | Mobile (iOS/Android/Flutter) |
|---------|-----|------------------------------|
| Location | Route (`/dashboard`) | Screen (`DashboardView`) |
| Navigation | URL change | Push/pop, tab switch |
| Entry point | `app/` or `pages/` directory | App launch, deeplink |

The journey map uses "screen" in the `screen` field regardless of platform -- for web apps this is the component/page name, for mobile it's the view/screen name.

## Error Handling

- No UI framework detected -- specify in `<testDir>/pathfinder/config.json` or install one.
- Journey map missing -- run `/map` first.
- Coverage drops after code changes -- new untested routes/screens. Re-run `/map`.
- Mermaid parse errors -- labels with parentheses `()` are auto-escaped to `[]`; all labels are double-quoted.
