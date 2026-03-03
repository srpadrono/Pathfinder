# Pathfinder

An expedition-based TDD workflow for AI coding agents with **automated UI test generation** for any tech stack.

## What It Does

Point Pathfinder at any project — it detects your UI framework, generates test skeletons with correct selectors and waits, and enforces a disciplined development cycle through git hooks.

**Supported frameworks:** Playwright, Cypress, Maestro, Detox, XCUITest, Espresso, Flutter integration tests.

## Quick Start

```bash
git clone https://github.com/srhenrybot-hub/superpowers.git ~/.pathfinder
cd your-project
git config core.hooksPath ~/.pathfinder/.githooks

# Initialize expedition
python3 ~/.pathfinder/scripts/pathfinder-init.py my-feature
```

Then: `/survey` → `/plan` → `/scout` → `/build` → `/report`

## Workflow

| Phase | What happens | Enforced by |
|-------|-------------|-------------|
| **Survey** | Explore requirements, get design approval | `survey.json` gate |
| **Plan** | Break into task files with dependencies | `plan.json` + `tasks/*.json` |
| **Scout** | Generate failing UI + unit tests (RED) | `scout.json` gate |
| **Build** | Implement minimal code to pass tests (GREEN) | `build.json` gate |
| **Report** | Verify, compute quality score, create PR | `report.json` gate |

**Phases cannot be skipped.** Git hooks block:
- Source code changes during survey/plan/scout
- Build gate without scout gate
- Push to main/master

## UI Test Generation

```bash
# Detect framework
python3 skills/ui-testing/scripts/detect-ui-framework.py .
# → {"uiFramework": "playwright", "platform": "web", "unitRunner": "vitest"}

# Generate test skeleton
python3 skills/ui-testing/scripts/generate-ui-test.py FEAT-01 "User can login" playwright --route /login
# → e2e/feat_01.spec.ts with correct imports, selectors, waits

# Visual regression
python3 skills/ui-testing/scripts/snapshot-compare.py capture login screenshot.png
python3 skills/ui-testing/scripts/snapshot-compare.py compare login new-screenshot.png
```

Framework-specific patterns (selectors, waits, assertions) in `skills/ui-testing/references/`.

## Quality Score (0-100)

| Criterion | Points |
|-----------|--------|
| All tests pass | 25 |
| Evidence complete | 15 |
| No regressions | 20 |
| Branch hygiene | 10 |
| PR created | 10 |
| All verified | 10 |
| Documentation | 10 |

🟢 90+: Merge-ready · 🟡 70-89: Review carefully · 🔴 <70: Fix first

## Structure

```
skills/
  surveying/          # Requirements + design approval
  planning/           # Task files + dependency graphs
  scouting/           # Write failing tests (RED)
  building/           # Implement to pass tests (GREEN)
  reporting/          # Verify + quality score + PR
  ui-testing/         # Framework detection + test generation
    references/       # Playwright, Cypress, Maestro, Detox, XCUITest, Espresso, Flutter
    scripts/          # detect-ui-framework.py, generate-ui-test.py, snapshot-compare.py
  using-pathfinder/   # Entry point + quick reference
scripts/              # pathfinder-init.py, check-deps, verify-expedition, etc.
hooks/                # Session start hook
```

7 skills · 8 scripts · 7 framework references · ~1,500 lines total

## Requirements

- Git
- Python 3
- `gh` CLI (for PR creation)

## License

MIT
