---
name: pathfinder
description: "Maps user journeys in any codebase, visualizes test coverage with Mermaid flowcharts and decision trees (✅/❌/⚠️), tracks coverage over time with before/after comparison, and generates framework-correct UI tests to fill gaps. Use when understanding or improving UI test coverage on an existing project. Supports Playwright, Cypress, Maestro, Detox, XCUITest, Espresso, Flutter. Do not use for unit tests, API tests, or greenfield projects with no code."
---

# Pathfinder

Map every user journey. See what's tested. Fill the gaps. Track progress.

## Quick Start

```bash
python3 scripts/pathfinder-init.py
```

## Workflow

```
/map → /blaze → /scout → /summit
```

| Command | Phase | What happens | Reference |
|---------|-------|-------------|-----------|
| `/map` | 🗺️ Map | Crawl code, discover all user journeys | [references/mapping.md](references/mapping.md) |
| `/blaze` | 🔥 Blaze | Generate Mermaid flowcharts, decision tree, and coverage delta | [references/blazing.md](references/blazing.md) |
| `/scout` | 🔭 Scout | Write UI tests for ❌ steps | [references/scouting.md](references/scouting.md) |
| `/summit` | ⛰️ Summit | Run tests, compare before/after, finalize coverage | [references/summiting.md](references/summiting.md) |

**When a command is invoked, read the matching reference file and follow its instructions.**

## Diagram Features

### Per-Journey Flowcharts
Each journey gets its own Mermaid flowchart with colour-coded nodes:
- 🟢 **Tested** — step has a passing UI test
- 🟡 **Partial** — test written but disabled or implicitly covered
- 🔴 **Untested** — no UI test coverage

### Combined Decision Tree
All journeys merged into a single flowchart showing every branching path:
- 🔵 **Diamond nodes** at decision points (e.g., user taps Confirm vs Decline)
- ⚡ **Dashed error arrows** branching from API/loading steps
- Shared prefixes are merged so you can spot gaps at a glance

### Before/After Comparison
When a baseline exists, diagrams show:
- **📸 Before (Baseline)** — decision tree at the time coverage work started
- **🚀 After (Current)** — decision tree with current coverage
- **📊 Coverage Delta** — table showing per-journey step changes

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

All scripts are Python 3 CLIs. They output JSON to stdout, errors to stderr.

| Script | Purpose |
|--------|---------|
| `scripts/pathfinder-init.py` | Initialize Pathfinder in a project |
| `scripts/scan-test-coverage.py .` | Scan existing tests and map to routes |
| `scripts/detect-ui-framework.py .` | Auto-detect UI test framework |
| `scripts/generate-ui-test.py ID "desc" framework --auto` | Generate or append a UI test |
| `scripts/generate-diagrams.py journeys.json` | Generate flowcharts, decision tree, and delta |
| `scripts/generate-diagrams.py journeys.json --save-baseline` | Reset baseline to current state |
| `scripts/generate-diagrams.py journeys.json --clear-baseline` | Remove baseline (next run creates fresh one) |
| `scripts/coverage-score.py [journeys.json]` | Compute coverage percentage |
| `scripts/snapshot-compare.py capture\|compare name image` | Visual regression |

## Project Files

| File | Purpose |
|------|---------|
| `$PATHFINDER_DIR/config.json` | Project config (framework, test directory, auth) |
| `$PATHFINDER_DIR/journeys.json` | Journey map — source of truth |
| `$PATHFINDER_DIR/journeys-baseline.json` | Baseline snapshot for before/after comparison (auto-created) |
| `$PATHFINDER_DIR/blazes.md` | Mermaid coverage diagrams (auto-generated) |

## Configuration

Optional `$PATHFINDER_DIR/config.json`:

```json
{
  "project": "my-app",
  "framework": "playwright",
  "testDir": "e2e/tests",
  "auth": { "storageState": "e2e/.auth/user.json" }
}
```

If absent, Pathfinder auto-detects from framework config files.
`PATHFINDER_DIR` defaults to `.pathfinder` and can point to a module-level folder.

## Error Handling

- No UI framework detected → specify in `$PATHFINDER_DIR/config.json` or install one.
- Journey map missing → run `/map` first.
- Coverage drops after code changes → new untested routes. Re-run `/map`.
- Mermaid parse errors → labels with parentheses `()` are auto-escaped to `[]`; all labels are double-quoted.
