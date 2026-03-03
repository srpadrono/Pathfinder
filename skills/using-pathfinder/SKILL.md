---
name: using-pathfinder
description: "Establishes expedition-based TDD workflow with automated UI test generation for any tech stack. Use when starting feature work that needs structured development with UI test coverage. Do not use for quick fixes, hotfixes, or tasks under 30 minutes."
---

# Using Pathfinder

Pathfinder enforces disciplined development through phase gates, automated UI test generation, and quality scoring. Supports Playwright, Cypress, Maestro, Detox, XCUITest, Espresso, and Flutter.

## Quick Start

```bash
python3 scripts/pathfinder-init.py <expedition-name>
```

Auto-detects your UI test framework and creates expedition state.

## Workflow

```
/survey → /plan → /scout → /build → /report
```

| Phase | Skill | What happens |
|-------|-------|-------------|
| Survey | `pathfinder:surveying` | Explore requirements, get design approval |
| Plan | `pathfinder:planning` | Break into task files with dependencies |
| Scout | `pathfinder:scouting` | Generate UI + unit tests (RED) via `pathfinder:ui-testing` |
| Build | `pathfinder:building` | Implement minimal code (GREEN) |
| Report | `pathfinder:reporting` | Verify, score, create PR |

**Phases cannot be skipped.** Git hooks enforce this.

## UI Testing

The `pathfinder:ui-testing` skill generates framework-correct test skeletons:

```bash
# Detect framework
python3 skills/ui-testing/scripts/detect-ui-framework.py .

# Generate test
python3 skills/ui-testing/scripts/generate-ui-test.py FEAT-01 "User can login" playwright

# Visual regression
python3 skills/ui-testing/scripts/snapshot-compare.py capture login-screen screenshot.png
```

Framework-specific patterns in `skills/ui-testing/references/<framework>.md`.

## Quick Reference

```bash
python3 scripts/pathfinder-init.py <name>              # init expedition
cat .pathfinder/state.json                              # status
bash scripts/pathfinder-check-deps.sh FEAT-01           # can I build this?
bash scripts/pathfinder-update-state.sh                 # sync state
bash scripts/verify-expedition.sh                       # quality score
```

## Error Handling

- Corrupted `state.json` → re-run `validate-tasks.py` and regenerate from task files.
- Git hooks block commit → check which phase gate is missing, complete it first.
- UI framework not detected → specify manually in `state.json.testRunners.e2e`.
