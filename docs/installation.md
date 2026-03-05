# Installation

Integrate Pathfinder into your project for Claude Code or Codex.

## Prerequisites

- Node.js 18+
- npm
- Git

## Quick Setup

### 1. Install Dependencies

```bash
npm install
npx playwright install --with-deps chromium
```

### 2. Environment

```bash
cp .env.example .env.local
# For the built-in demo server, defaults are already valid
# Edit .env.local only if testing against a real app/auth provider
```

Required environment variables:
- `BASE_URL` — Your app's URL (e.g., `http://localhost:3000`)
- `TEST_EMAIL` — Test account email
- `TEST_PASSWORD` — Test account password

Add to `.gitignore`:
```
.env.local
.auth/
test-results/
playwright-report/
```

### 3. Git Hooks

Install Pathfinder's git hooks for phase enforcement:

```bash
git config core.hooksPath .githooks
```

### 4. Diagnose

```bash
npm run doctor
```

## Platform Setup

### Claude Code

Claude Code discovers `.claude-plugin/` automatically. Clone or copy Pathfinder into your project:

```bash
# Clone into your project
git clone https://github.com/srpadrono/Pathfinder.git .pathfinder-skill

# Or add as a git submodule
git submodule add https://github.com/srpadrono/Pathfinder.git .pathfinder-skill
```

The SessionStart hook in `.claude-plugin/hooks/hooks.json` auto-injects the Pathfinder workflow at session start. Slash commands (`/survey`, `/scout`, `/build`, `/report`) are available immediately.

### Codex

See `.codex/INSTALL.md` for Codex-specific setup:

```bash
git clone https://github.com/srpadrono/Pathfinder.git ~/.codex/pathfinder
mkdir -p ~/.agents/skills
ln -s ~/.codex/pathfinder/skills ~/.agents/skills/pathfinder
```

Restart Codex to discover the skills.

## Running Tests

```bash
# E2E tests
npx playwright test

# Unit tests
npx vitest run

# Both layers
npm run test:all

# Single checkpoint
npx playwright test --grep "AUTH-01"

# Debug mode
npx playwright test --debug

# View HTML report
npx playwright show-report

# Validate everything (docs, pathfinder files, checkpoints, lint, unit)
npm run validate
```

## Directory Structure

```
project/
├── e2e/
│   ├── auth.setup.ts               # Auth state setup
│   ├── fixtures/pathfinder.ts       # Checkpoint fixture
│   └── reporters/pathfinder-reporter.ts
├── src/
│   └── **/*.test.ts                 # Co-located unit tests
├── scripts/
│   ├── verify-expedition.sh         # Quality score + report
│   ├── pathfinder-check-deps.sh     # Dependency checker
│   ├── pathfinder-update-state.sh   # State sync
│   ├── update-coverage.ts           # Coverage sync
│   └── generate-map.ts              # Trail map generation
├── templates/
│   ├── user-journeys.md
│   ├── test-file.ts
│   ├── state.json
│   └── task.json
├── references/
│   └── task-tracking.md             # Task file format and procedures
├── .pathfinder/
│   ├── state.json
│   └── tasks/
├── .claude-plugin/                  # Claude Code adapter
│   ├── hooks/hooks.json
│   └── commands/
├── .codex/                          # Codex adapter
│   └── INSTALL.md
├── .github/
│   ├── workflows/pathfinder.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── playwright.config.ts
├── vitest.config.ts
└── .env.local
```
