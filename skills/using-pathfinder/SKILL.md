---
name: using-pathfinder
description: "Maps user journeys in any codebase, visualizes test coverage with Mermaid diagrams, and generates UI tests to fill gaps. Use when understanding and improving UI test coverage on an existing project. Do not use for unit testing, API testing, or greenfield projects with no code."
---

# Using Pathfinder

Pathfinder discovers every user journey in a codebase, shows what's tested vs not with Mermaid diagrams, then generates the missing UI tests.

## Quick Start

```bash
python3 scripts/pathfinder-init.py
```

## Workflow

```
/map → /blaze → /scout → /summit
```

| Phase | Skill | What happens |
|-------|-------|-------------|
| Map | `pathfinder:mapping` | Deep dive into code, discover all user journeys |
| Blaze | `pathfinder:blazing` | Generate Mermaid diagrams: ✅ tested, ❌ untested |
| Scout | `pathfinder:scouting` | Write UI tests for ❌ steps via `pathfinder:ui-testing` |
| Summit | `pathfinder:summiting` | Run tests, update diagrams ❌→✅, compute coverage |

## Project Configuration

Create `.pathfinder/config.json` to customize test generation:

```json
{
  "testDir": "e2e/tests",
  "framework": "playwright",
  "unitRunner": "vitest",
  "filePattern": "{journey}.spec.ts",
  "auth": {
    "storageState": "e2e/.auth/user.json"
  }
}
```

The test generator reads this to match existing project patterns. If absent, it auto-detects from framework config files.

## Quick Reference

```bash
python3 scripts/pathfinder-init.py                                    # init
python3 skills/mapping/scripts/scan-test-coverage.py .                # scan tests
python3 skills/blazing/scripts/generate-diagrams.py .pathfinder/journeys.json  # diagrams
python3 skills/ui-testing/scripts/generate-ui-test.py AUTH-01 "Login" playwright --auto  # test
python3 scripts/coverage-score.py .pathfinder/journeys.json           # score
```

## Error Handling

- No UI framework detected → specify in `.pathfinder/config.json` or install one.
- Journey map missing → run `/map` first.
- Coverage drops → new code added untested routes. Re-run `/map`.
