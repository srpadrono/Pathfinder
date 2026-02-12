# Installation

Integrate Pathfinder into an existing project.

## Prerequisites

- Node.js 18+
- npm

## Quick Setup

### 1. Install Dependencies

```bash
npm install
npx playwright install chromium
```

### 2. Environment

Copy `.env.example` and fill in your values:

```bash
cp .env.example .env.local
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

### 3. Configuration

Pathfinder uses two config files:
- **`playwright.config.ts`** — E2E tests (projects, auth, reporters, webServer)
- **`vitest.config.ts`** — Unit tests (co-located in `src/**/*.test.ts`)

### 4. Git Hooks

Install Pathfinder's git hooks for phase enforcement:

```bash
git config core.hooksPath .githooks
```

## Running Tests

```bash
# E2E tests
npx playwright test

# Unit tests
npx vitest run

# Both
npm run test:all

# Single checkpoint
npx playwright test --grep "AUTH-01"

# Debug mode
npx playwright test --debug

# View HTML report
npx playwright show-report
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
│   ├── update-coverage.ts
│   └── generate-map.ts
├── templates/
│   ├── user-journeys.md
│   ├── test-file.ts
│   ├── state.json
│   └── task.json
├── .pathfinder/
│   ├── state.json
│   └── tasks/
├── .github/
│   ├── workflows/pathfinder.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── playwright.config.ts
├── vitest.config.ts
├── .auth/state.json
└── .env.local
```

## First Journey

### 1. Add to Trail Map

Edit `USER-JOURNEYS.md` (or copy from `templates/user-journeys.md`):

```markdown
## 🔐 Auth Journey

### Checkpoints
| ID | Checkpoint | Status |
|----|------------|--------|
| AUTH-01 | Login success | ❌ |
| AUTH-02 | Invalid password | ❌ |
```

### 2. Create Test File

Use `templates/test-file.ts` as a starting point:

```typescript
import { test, expect } from './fixtures/pathfinder';

test.describe('Auth Journey', () => {
  test('AUTH-01: Login redirects to dashboard', async ({ page, checkpoint }) => {
    checkpoint.mark('AUTH-01', 'Login redirects to dashboard');
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/dashboard/);
    checkpoint.clear('AUTH-01');
  });
});
```

### 3. Run

```bash
npx playwright test --grep "AUTH"
```

## Team Roles

| Role | Territory | Focus |
|------|-----------|-------|
| Scout | `e2e/`, `src/**/*.test.ts` | Tests + diagrams |
| Builder | `src/` | Implementation |
