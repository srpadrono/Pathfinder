---
name: using-pathfinder
description: "Maps user journeys in any codebase, visualizes test coverage with Mermaid diagrams, and generates UI tests to fill gaps. Use when you want to understand and improve UI test coverage on an existing project. Do not use for unit testing, API testing, or greenfield projects with no code."
---

# Using Pathfinder

Pathfinder discovers every user journey in your codebase, shows what's tested vs not with Mermaid diagrams, then generates the missing UI tests.

## Quick Start

```bash
python3 scripts/pathfinder-init.py
```

## Workflow

```
/map → /diagram → /scout → /verify
```

| Phase | Skill | What happens |
|-------|-------|-------------|
| Map | `pathfinder:mapping` | Deep dive into code, discover all user journeys |
| Diagram | `pathfinder:diagramming` | Generate Mermaid diagrams: ✅ tested, ❌ untested |
| Scout | `pathfinder:scouting` | Write UI tests for ❌ steps using `pathfinder:ui-testing` |
| Verify | `pathfinder:verifying` | Run tests, update diagrams ❌→✅, compute coverage |

## The Diagram Is the Source of Truth

```mermaid
journey
    title 🔐 Authentication
    section Login
      Open login page: 3: ❌
      Enter credentials: 5: ✅
      See dashboard: 5: ✅
    section Logout
      Tap logout: 3: ❌
```

Every time you write a test, the diagram updates. Coverage percentage goes up. Gaps become visible.

## Quick Reference

```bash
python3 scripts/pathfinder-init.py                                    # init
python3 skills/mapping/scripts/scan-test-coverage.py .                # scan existing tests
python3 skills/diagramming/scripts/generate-diagrams.py .pathfinder/journeys.json  # diagrams
python3 skills/ui-testing/scripts/generate-ui-test.py AUTH-01 "Login" playwright    # generate test
python3 scripts/coverage-score.py .pathfinder/journeys.json           # coverage score
```

## Error Handling

- No UI framework detected → specify manually or install one.
- Journey map missing → run `/map` first.
- Coverage drops → new code added untested routes. Re-run `/map`.
