---
name: using-pathfinder
description: "Establishes expedition-based TDD workflow with phase enforcement on top of Superpowers skills. Use when starting feature work that benefits from structured survey-plan-scout-build-report phases. Do not use for quick fixes, hotfixes, or tasks under 30 minutes."
---

<EXTREMELY-IMPORTANT>
You have Pathfinder — an expedition-based TDD workflow built on top of Superpowers.

If a Superpowers skill applies to your task, you MUST use it. Pathfinder adds structure and enforcement on top.
</EXTREMELY-IMPORTANT>

# Using Pathfinder

Pathfinder wraps Superpowers' composable skills with an expedition metaphor that enforces disciplined software development through phase gates, task tracking, and quality scoring.

## How Skills Work

Pathfinder skills are loaded on demand. When you encounter a task that matches a skill's trigger, invoke it. Superpowers skills handle the actual work; Pathfinder skills add structure.

### Pathfinder Skills (expedition structure)
| Skill | Trigger | What it does |
|-------|---------|-------------|
| `pathfinder:surveying` | `/survey` or starting a new feature | Wraps brainstorming + creates expedition state |
| `pathfinder:planning` | After survey approval | Wraps writing-plans + creates task files |
| `pathfinder:scouting` | `/scout` or after planning | Wraps TDD (RED phase) + captures failure evidence |
| `pathfinder:building` | `/build` or after scouting | Wraps subagent-driven-dev (GREEN phase) + dependency checks |
| `pathfinder:reporting` | `/report` or after building | Wraps verification + finishing + quality score |

### Superpowers Skills (actual work)
All Superpowers skills remain available:
- `superpowers:brainstorming` — collaborative design
- `superpowers:writing-plans` — implementation planning
- `superpowers:test-driven-development` — RED-GREEN-REFACTOR
- `superpowers:subagent-driven-development` — dispatch fresh agents per task
- `superpowers:executing-plans` — batch execution with checkpoints
- `superpowers:requesting-code-review` — two-stage review
- `superpowers:receiving-code-review` — technical evaluation
- `superpowers:systematic-debugging` — root cause analysis
- `superpowers:verification-before-completion` — evidence before claims
- `superpowers:finishing-a-development-branch` — merge/PR/cleanup
- `superpowers:using-git-worktrees` — isolated workspaces
- `superpowers:dispatching-parallel-agents` — concurrent independent tasks
- `superpowers:writing-skills` — create new skills

## Expedition Workflow

```
/survey → /scout → /build → /report
   │         │        │        │
   ▼         ▼        ▼        ▼
 survey   planning  scouting  reporting
 .json    + tasks   (RED)     (verify + PR)
          .json     building
                    (GREEN)
```

### Phase Ordering (ENFORCED)
1. **Survey** — Understand the problem, explore approaches, get design approval
2. **Plan** — Break design into bite-sized tasks with dependencies
3. **Scout** — Write ALL failing tests (RED phase of TDD)
4. **Build** — Implement minimal code to pass tests (GREEN phase)
5. **Report** — Verify independently, compute quality score, create PR

**You cannot skip phases.** Git hooks and state files enforce this:
- No source code changes during survey/plan/scout phases
- No build gate without scout gate
- No report gate without build gate
- No push to main/master (feature branches only)

## Resuming an Expedition

On session start, check for `.pathfinder/state.json`:
- If it exists, read it and announce current phase + progress
- If not, you're starting fresh — wait for `/survey` or a feature request

## Test Runner Configuration

Pathfinder is test-framework agnostic. During survey, detect the project type and set runners in `state.json`:

```json
{
  "testRunners": {
    "e2e": "playwright",
    "unit": "vitest"
  }
}
```

| Project type | e2e | unit |
|-------------|-----|------|
| Next.js / React web | `playwright` | `vitest` |
| React Native / Expo | `maestro` | `jest` |
| FastAPI / Django | `pytest` | `pytest` |
| Native iOS | `xcuitest` | `xctest` |
| Native Android | `espresso` | `gotest` |

Read `testRunners` from `state.json` before running any test commands. See `docs/test-runners.md` for the full command reference per framework.

## Quick Reference

```bash
# Check expedition status
cat .pathfinder/state.json

# Check a specific checkpoint
cat .pathfinder/tasks/FEAT-01.json

# Verify dependencies before building
bash scripts/pathfinder-check-deps.sh FEAT-01

# Update state from task files
bash scripts/pathfinder-update-state.sh

# Run full expedition verification + quality score
bash scripts/verify-expedition.sh
```

## Anti-Rationalization

| Temptation | Why it's wrong | What to do |
|------------|---------------|-----------|
| "This is simple, skip survey" | Simple projects have unexamined assumptions | Survey can be brief, but do it |
| "I'll write tests after" | You won't know if tests catch the right thing | RED before GREEN, always |
| "Dependencies don't matter here" | They prevent cascading failures | Check deps, always |
| "I know the tests pass" | Memory is unreliable | Run them. Capture evidence. |
| "PR can wait" | Unmerged work is invisible work | Report phase is not optional |

## Error Handling
* If `.pathfinder/state.json` is corrupted or missing required fields, re-run `python3 scripts/validate-tasks.py` and regenerate state from task files.
* If git hooks block a commit, check which phase gate is missing and complete that phase first.
* If the expedition branch has diverged from main, rebase before reporting: `git rebase main`.
