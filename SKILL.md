---
name: pathfinder
description: "Maps user journeys in any codebase, visualizes test coverage with Mermaid diagrams (✅/❌), and generates framework-correct UI tests to fill gaps. Use when understanding or improving UI test coverage on an existing project. Supports Playwright, Cypress, Maestro, Detox, XCUITest, Espresso, Flutter. Do not use for unit tests, API tests, or greenfield projects with no code."
---

# Pathfinder

Map every user journey. See what's tested. Fill the gaps.

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
| `/blaze` | 🔥 Blaze | Generate Mermaid diagrams: ✅ tested, ❌ untested | [references/blazing.md](references/blazing.md) |
| `/scout` | 🔭 Scout | Write UI tests for ❌ steps | [references/scouting.md](references/scouting.md) |
| `/summit` | ⛰️ Summit | Run tests, update diagrams ❌→✅, coverage score | [references/summiting.md](references/summiting.md) |

**When a command is invoked, read the matching reference file and follow its instructions.**

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
| `scripts/generate-diagrams.py .pathfinder/journeys.json` | Generate Mermaid coverage diagrams |
| `scripts/coverage-score.py .pathfinder/journeys.json` | Compute coverage percentage |
| `scripts/snapshot-compare.py capture\|compare name image` | Visual regression |

## Project Files

| File | Purpose |
|------|---------|
| `.pathfinder/config.json` | Project config (framework, test directory, auth) |
| `.pathfinder/journeys.json` | Journey map — source of truth |
| `.pathfinder/blazes.md` | Mermaid coverage diagrams (auto-generated) |

## Configuration

Optional `.pathfinder/config.json`:

```json
{
  "project": "my-app",
  "framework": "playwright",
  "testDir": "e2e/tests",
  "auth": { "storageState": "e2e/.auth/user.json" }
}
```

If absent, Pathfinder auto-detects from framework config files.

## Error Handling

- No UI framework detected → specify in `.pathfinder/config.json` or install one.
- Journey map missing → run `/map` first.
- Coverage drops after code changes → new untested routes. Re-run `/map`.
