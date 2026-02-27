# AGENTS.md — Pathfinder Workflow

**Universal agent instructions for Test-Driven Development using the Pathfinder methodology.**

Works with any AI coding assistant: Claude Code, OpenClaw, OpenCode, Codex, Cursor, or direct LLM context.

---

## Platform Support

Pathfinder works with any AI coding assistant. Platform-specific adapters provide automatic bootstrap:

| Platform | Adapter | Install |
|----------|---------|---------|
| Claude Code | `.claude-plugin/` (hooks + commands) | Automatic via SessionStart hook |
| OpenClaw | Root `SKILL.md` + `.claude-plugin/` | Install via skill marketplace |
| OpenCode | `.opencode/` (plugin + install) | See `.opencode/INSTALL.md` |
| Codex | `.codex/` (install) | See `.codex/INSTALL.md` |
| Other | Read `AGENTS.md` + `skills/` directly | Manual — load `skills/using-pathfinder/SKILL.md` first |

Cross-platform tool mapping is in `skills/using-pathfinder/SKILL.md`.

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
| `pathfinder:planning` | Journey map + checkpoint extraction | 2. Plan |
| `pathfinder:scouting` | Writing failing tests (RED) | 3. Scout |
| `pathfinder:unit-testing` | Unit tests for `src/` code | 3. Scout |
| `pathfinder:building` | Implementing to pass tests (GREEN) | 4. Build |
| `pathfinder:reporting` | PR with evidence | 5. Report |
| `pathfinder:dispatching` | Multi-agent coordination | Cross-cutting |
| `pathfinder:git-workflow` | Branching/commit/PR workflow | Cross-cutting |
| `pathfinder:code-review` | Structured code review | Cross-cutting |
| `pathfinder:security` | Security review and hardening checks | Cross-cutting |
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
2. **Plan** — Create journey map + checkpoints + task files
3. **Scout** — Write ALL tests first, verify they FAIL, update to 🔄
4. **Build** — Minimal code, one test at a time, update to ✅
5. **Report** — Verify evidence, run full checks, create PR
6. **Dispatch (optional)** — Fresh context, two-stage review for large changes

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
| `.claude-plugin/hooks/hooks.json` | SessionStart hook configuration (Claude Code) |
| `.claude-plugin/commands/` | Slash command definitions (Claude Code) |
| `.opencode/` | OpenCode adapter (plugin + install) |
| `.codex/` | Codex adapter (install) |
| `SKILL.md` | OpenClaw marketplace metadata |
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
