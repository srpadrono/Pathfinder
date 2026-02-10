# AGENTS.md — Pathfinder Workflow

**Universal agent instructions for Test-Driven Development using the Pathfinder methodology.**

Works with any AI coding assistant: OpenClaw, Claude Code, Codex, Cursor, or direct LLM context.

---

## What is Pathfinder?

Pathfinder is a TDD workflow using an expedition metaphor:
- **Scouts** survey, chart maps, and write tests (❌ → 🔄)
- **Builders** implement features until tests pass (🔄 → ✅)

**Core insight:** Role separation enforces true test-first development.

**Philosophy:**
- **Test-Driven** — Write tests first, always
- **Systematic over ad-hoc** — Process over guessing
- **YAGNI ruthlessly** — Remove unnecessary features from all designs
- **Evidence over claims** — Verify before declaring success
- **Complexity reduction** — Simplicity as primary goal

---

## Skills Architecture

Pathfinder uses composable skills (inspired by [obra/superpowers](https://github.com/obra/superpowers)).
Each skill is a focused Markdown file in the `skills/` directory.

### THE RULE

If there is even a 1% chance a Pathfinder skill applies to your current task,
you MUST invoke it. This is not optional.

### Available Skills

| Skill | Purpose | Phase |
|-------|---------|-------|
| `pathfinder:surveying` | Socratic requirements gathering | 1. Survey |
| `pathfinder:charting` | Mermaid trail map creation | 2. Chart |
| `pathfinder:marking` | Checkpoint extraction + edge cases | 3. Mark |
| `pathfinder:scouting` | Writing failing tests (RED) | 4. Scout |
| `pathfinder:building` | Implementing to pass tests (GREEN) | 5. Build |
| `pathfinder:dispatching` | Multi-agent coordination | 6. Dispatch |
| `pathfinder:reporting` | PR with evidence | 7. Report |
| `pathfinder:test-driven-development` | Core TDD enforcement | Cross-cutting |
| `pathfinder:verification-before-completion` | Evidence-based verification | Cross-cutting |
| `pathfinder:systematic-debugging` | Root-cause debugging | Cross-cutting |

### Slash Commands

| Command | Action |
|---------|--------|
| `/survey` | Start requirements gathering |
| `/scout` | Enter Scout mode (write tests) |
| `/build` | Enter Builder mode (implement) |
| `/report` | Generate expedition report |

---

## Quick Reference

### Start a New Journey

1. **Survey** — Socratic questions, one at a time
2. **Chart** — Mermaid diagram with ❌, present in sections
3. **Mark** — Checkpoint list + edge case matrix
4. **Scout** — Write ALL tests, verify they FAIL, update to 🔄
5. **Build** — Minimal code, one test at a time, update to ✅
6. **Dispatch** — Fresh context, two-stage review
7. **Report** — PR with evidence, severity-based issues

### Playwright CLI Commands

| Phase | Command |
|-------|---------|
| Scout (codegen) | `npx playwright codegen --load-storage=.auth/state.json <url>` |
| Scout (verify RED) | `npx playwright test --grep "FEAT-XX" --reporter=list` |
| Build (verify GREEN) | `npx playwright test --grep "FEAT-XX" --reporter=list` |
| Build (debug) | `npx playwright test --grep "FEAT-XX" --debug` |
| Build (trace) | `npx playwright show-trace test-results/<test>/trace.zip` |
| Report (full suite) | `npx playwright test --reporter=list` |
| Report (HTML) | `npx playwright test --reporter=html && npx playwright show-report` |
| Coverage | `npm run test:coverage && npm run test:generate-map` |

### Key Principles

- Tests exist before implementation. Always.
- Wrote code before test? Delete it.
- One question at a time. One test at a time.
- YAGNI ruthlessly. Minimal code only.
- Critical issues block progress.
- Evidence over claims. Run the test.

---

## Trail Markers

| Marker | Name | Meaning |
|--------|------|---------|
| ❌ | Uncharted | Checkpoint identified, no test yet |
| 🔄 | Scouted | Test written, awaiting implementation |
| ✅ | Cleared | Test passing |
| ⚠️ | Unstable | Flaky test needs attention |
| ⏭️ | Skipped | Out of scope for this expedition |

---

## Role Separation

### Scout Role

**Responsibilities:** Survey terrain, chart maps, mark trails, write tests (❌ → 🔄)
**Territory:** `e2e/`, `USER-JOURNEYS.md`, test files
**Forbidden:** Modifying `src/` (implementation code)

### Builder Role

**Responsibilities:** Follow marked trail, implement minimal code (🔄 → ✅), collect evidence
**Territory:** `src/`, implementation code
**Forbidden:** Modifying test assertions

---

## File Locations

| File | Purpose |
|------|---------|
| `skills/` | Composable skill definitions |
| `hooks/hooks.json` | SessionStart hook configuration |
| `commands/` | Slash command definitions |
| `e2e/` | Playwright test files |
| `e2e/fixtures/pathfinder.ts` | Checkpoint tracking fixture |
| `e2e/reporters/pathfinder-reporter.ts` | Trail map update reporter |
| `playwright.config.ts` | Playwright configuration |
| `checkpoints.json` | Checkpoint state (source of truth) |
| `USER-JOURNEYS.md` | Generated trail map |
| `templates/` | Templates for tests, PRs, journeys |

---

## Environment Setup

Create `.env.local`:
```bash
TEST_EMAIL=test@example.com
TEST_PASSWORD=your-test-password
BASE_URL=http://localhost:3000
```

**Never commit credentials.** Use environment variables.
