---
name: using-pathfinder
description: "Establishes expedition-based TDD workflow with phase enforcement. Use when starting feature work that benefits from structured survey-plan-scout-build-report phases. Do not use for quick fixes, hotfixes, or tasks under 30 minutes."
---

# Using Pathfinder

Pathfinder enforces disciplined development through phase gates, task tracking, and quality scoring.

## Workflow

```
/survey → /plan → /scout → /build → /report
```

| Phase | Skill | What happens |
|-------|-------|-------------|
| Survey | `pathfinder:surveying` | Explore requirements, get design approval |
| Plan | `pathfinder:planning` | Break into task files with dependencies |
| Scout | `pathfinder:scouting` | Write ALL failing tests (RED) |
| Build | `pathfinder:building` | Implement minimal code (GREEN) |
| Report | `pathfinder:reporting` | Verify, score, create PR |

**Phases cannot be skipped.** Git hooks enforce this.

## Resuming

On session start, check for `.pathfinder/state.json`. If it exists, announce current phase and progress.

## Test Runners

Configured in `state.json.testRunners` during survey. See `docs/test-runners.md` for commands per framework.

## Quick Reference

```bash
cat .pathfinder/state.json                        # expedition status
cat .pathfinder/tasks/FEAT-01.json                # checkpoint detail
bash scripts/pathfinder-check-deps.sh FEAT-01     # can I build this?
bash scripts/pathfinder-update-state.sh            # sync state from tasks
bash scripts/verify-expedition.sh                  # full verification + score
python3 scripts/validate-tasks.py .pathfinder/tasks  # validate task files
```

## Error Handling

- Corrupted `state.json` → re-run `validate-tasks.py` and regenerate from task files.
- Git hooks block commit → check which phase gate is missing, complete it first.
- Branch diverged from main → rebase before reporting.
