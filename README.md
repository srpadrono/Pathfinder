<p align="center">
  <img src="assets/banner.png" alt="Pathfinder Banner" width="100%">
</p>

<p align="center">
  <strong>Marks the trail before others follow.</strong>
</p>

<p align="center">
  <em>A TDD workflow skill for AI coding agents using an expedition metaphor.</em>
</p>

<p align="center">
  <a href="https://github.com/srpadrono/Pathfinder/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
  <a href="https://github.com/srpadrono/Pathfinder">
    <img src="https://img.shields.io/badge/AI_Agent-Skill-green.svg" alt="AI Agent Skill">
  </a>
  <a href="https://playwright.dev/">
    <img src="https://img.shields.io/badge/Playwright-CLI-orange.svg" alt="Playwright">
  </a>
</p>

---

## What is Pathfinder?

Pathfinder is a **TDD methodology packaged as an AI agent skill**. It uses an expedition metaphor to enforce disciplined test-driven development:

- **Scouts** survey terrain, chart maps, and write failing tests (❌ → 🔄)
- **Builders** implement minimal code until tests pass (🔄 → ✅)

Built on [Playwright CLI](https://playwright.dev/docs/test-cli) and inspired by [obra/superpowers](https://github.com/obra/superpowers).

## Features

- **5-Phase Workflow** — Survey → Plan → Scout → Build → Report (canonical)
- **Composable Skills** — 12 focused skills loaded on-demand from `skills/`
- **SessionStart Hook** — Auto-injects workflow at session start
- **Slash Commands** — `/survey`, `/scout`, `/build`, `/report`
- **Anti-Rationalization** — Explicit guards against skipping TDD
- **Playwright CLI Integration** — `codegen`, `test`, `show-report`, `show-trace`
- **Checkpoint Fixture** — Custom Playwright fixture for trail marker tracking
- **Custom Reporter** — Outputs `test-results/checkpoints.json` for trail map updates
- **Evidence Verification** — No claims without proof
- **Two-Stage Review** — Trail compliance + code quality reviews
- **Fresh Context Dispatch** — Complete templates for Scout/Builder subagents
- **CI/CD Ready** — GitHub Actions workflow included

## Quick Start

### 1. Install

```bash
npm install
npx playwright install --with-deps chromium
```

### 2. Configure

```bash
cp .env.example .env.local
# For built-in demo server, defaults are already valid
# Edit .env.local only if testing against a real app/auth provider
```

### 3. Use with AI Agent

The `AGENTS.md` file provides universal instructions. The `skills/` directory contains composable skills that are loaded on-demand.

**Start a new feature:**
```
/survey    → Gather requirements
/scout     → Write tests
/build     → Implement
/report    → Create PR
```

### 4. Run Tests

```bash
# Diagnose environment
npm run doctor

# Run all tests (auto-starts demo server)
npx playwright test

# Run specific checkpoint
npx playwright test --grep "AUTH-01"

# Debug a test
npx playwright test --grep "AUTH-01" --debug

# Generate test from recording
npx playwright codegen --load-storage=.auth/state.json http://localhost:3000

# View HTML report
npx playwright show-report

# View failure trace
npx playwright show-trace test-results/<test>/trace.zip

# Validate docs + pathfinder files + lint + unit
npm run validate

# Validate checkpoint report schema
npm run validate:checkpoints

# Update coverage
npm run test:coverage

# Generate trail map
npm run test:generate-map
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  ENFORCEMENT LAYER                   │
│  hooks/hooks.json → skills/using-pathfinder/         │
│  Anti-rationalization, "The Rule", verification      │
├─────────────────────────────────────────────────────┤
│                  METHODOLOGY LAYER                   │
│  skills/ (composable), commands/ (slash)             │
│  Survey → Plan → Scout → Build → Report              │
├─────────────────────────────────────────────────────┤
│                  INTEGRATION LAYER                   │
│  e2e/fixtures/pathfinder.ts (checkpoint fixture)     │
│  e2e/reporters/pathfinder-reporter.ts (reporter)     │
│  playwright.config.ts (projects, auth, evidence)     │
├─────────────────────────────────────────────────────┤
│                  TOOLING LAYER                       │
│  scripts/ (coverage, map generation)                 │
│  templates/ (user-journeys, tests, PR)               │
├─────────────────────────────────────────────────────┤
│                  PLATFORM LAYER                      │
│  npx playwright test/codegen/show-report/show-trace  │
│  @playwright/test, Node.js, TypeScript               │
└─────────────────────────────────────────────────────┘
```

## Repository Structure

```
pathfinder/
├── package.json                    # Dependencies and scripts
├── tsconfig.json                   # TypeScript configuration
├── playwright.config.ts            # Playwright config with projects
├── .gitignore                      # Ignore credentials, node_modules, results
├── AGENTS.md                       # Universal agent instructions (concise)
├── SKILL.md                        # OpenClaw/skill marketplace metadata
├── PROPOSAL.md                     # Improvement proposal and roadmap
├── skills/                         # Composable skills (Superpowers-inspired)
│   ├── using-pathfinder/SKILL.md   #   Meta-skill: routing + enforcement
│   ├── surveying/SKILL.md          #   Phase 1: Requirements gathering
│   ├── planning/SKILL.md           #   Phase 2: Journey map + checkpoints
│   ├── scouting/SKILL.md           #   Phase 3: Failing tests (RED)
│   ├── unit-testing/SKILL.md       #   Unit tests for src/ code
│   ├── building/SKILL.md           #   Phase 4: Implementation (GREEN)
│   ├── reporting/SKILL.md          #   Phase 5: Evidence + PR
│   ├── dispatching/SKILL.md        #   Multi-agent coordination
│   ├── git-workflow/SKILL.md       #   Branching/commit/PR workflow
│   ├── code-review/SKILL.md        #   Structured review checklist
│   ├── security/SKILL.md           #   Security checks
│   └── systematic-debugging/SKILL.md # Root-cause debugging
├── hooks/hooks.json                # SessionStart hook config
├── commands/                       # Slash commands
│   ├── survey.md                   #   /survey
│   ├── scout.md                    #   /scout
│   ├── build.md                    #   /build
│   └── report.md                   #   /report
├── e2e/                            # Playwright test files
│   ├── auth.setup.ts               #   Auth state setup
│   ├── example.spec.ts             #   Example test with checkpoints
│   ├── fixtures/pathfinder.ts      #   Checkpoint tracking fixture
│   └── reporters/pathfinder-reporter.ts  # Trail map reporter
├── scripts/
│   ├── update-coverage.ts          #   JSON-based coverage sync
│   └── generate-map.ts             #   Generate USER-JOURNEYS.md
├── templates/                      # Templates for new projects
│   ├── user-journeys.md            #   Trail map template
│   ├── test-file.ts                #   Test file template
│   ├── state.json                  #   Expedition state template
│   └── task.json                   #   Task/checkpoint template
├── .github/
│   ├── workflows/pathfinder.yml    #   CI/CD workflow
│   └── PULL_REQUEST_TEMPLATE.md    #   PR template
├── docs/                           # Reference documentation
└── assets/                         # Branding (banner, logo)
```

## Canonical Workflow

- Source of truth: [`docs/architecture/canonical-workflow.md`](docs/architecture/canonical-workflow.md)

## Deterministic Demo

Pathfinder now includes a built-in demo server used by Playwright via `webServer`.

- Server entrypoint: `scripts/demo-server.mjs`
- Health endpoint: `http://127.0.0.1:3000/health`
- Manual run: `npm run test:demo-server`

## Trail Markers

| Marker | Name | Meaning |
|--------|------|---------|
| ❌ | Uncharted | Checkpoint identified, no test yet |
| 🔄 | Scouted | Test written, awaiting implementation |
| ✅ | Cleared | Test passing |
| ⚠️ | Unstable | Flaky test needs attention |
| ⏭️ | Skipped | Out of scope for this expedition |

## Task-Level Tracking (v0.4.0)

Pathfinder v0.4.0 introduces **structural enforcement** — making phase violations physically impossible rather than relying on voluntary discipline.

### Task Files

Each checkpoint gets its own JSON file in `.pathfinder/tasks/`:

```
.pathfinder/
├── state.json              # Current phase + expedition metadata
├── tasks/
│   ├── FEAT-01.json        # Individual checkpoint with status & evidence
│   ├── FEAT-02.json
│   └── ...
└── report.json             # Quality score from verification
```

**Status lifecycle:** `planned` → `red` → `green` → `verified`

### Dependency Enforcement

Checkpoints declare dependencies. The builder cannot work on a blocked checkpoint:

```bash
bash scripts/pathfinder-check-deps.sh FEAT-03
# ✘ Blocked: FEAT-03 depends on FEAT-01 (status: red)
```

### Verification & Quality Score

`verify-expedition.sh` computes a 0-100 quality score:

| Criterion | Points |
|-----------|--------|
| All checkpoint tests pass | 25 |
| Evidence complete | 20 |
| No regressions | 20 |
| Branch hygiene | 15 |
| PR created | 10 |
| All verified | 10 |

**Thresholds:** 90+ merge-ready, 70-89 review carefully, <70 fix issues.

### New Scripts

| Script | Purpose |
|--------|---------|
| `scripts/pathfinder-check-deps.sh` | Check if a checkpoint's dependencies are satisfied |
| `scripts/pathfinder-update-state.sh` | Sync state.json checkpoint counts from task files |
| `scripts/verify-expedition.sh` | Full verification with quality score |

### Git Hooks

| Hook | Purpose |
|------|---------|
| `.githooks/pre-commit` | Reads state.json, blocks src/ changes in wrong phase |
| `.githooks/post-commit` | Auto-updates state.json after every commit |
| `.githooks/pre-push` | Blocks direct push to main/master |

Install: `git config core.hooksPath .githooks`


## Improvement Roadmap

- See the execution backlog: [`docs/world-class-roadmap.md`](docs/world-class-roadmap.md)


## Governance

- CODEOWNERS: [`.github/CODEOWNERS`](.github/CODEOWNERS)
- ADR template: [`docs/adr/template.md`](docs/adr/template.md)
- Release checklist: [`docs/release-checklist.md`](docs/release-checklist.md)

## Inspiration

- [obra/superpowers](https://github.com/obra/superpowers) — Composable skills architecture, SessionStart hooks, anti-rationalization tables, TDD enforcement, verification-before-completion
- [Playwright CLI](https://playwright.dev/docs/test-cli) — Native test runner, codegen, show-report, show-trace, custom fixtures and reporters
- [@playwright/cli](https://testdino.com/blog/playwright-cli/) — Token-efficient browser automation for AI agents

## License

MIT
