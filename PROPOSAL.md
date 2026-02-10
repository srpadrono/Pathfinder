# Pathfinder Improvement Proposal

**Date:** 2026-02-10
**Author:** Automated Deep Analysis
**Scope:** Architecture, code quality, testing patterns, tooling, documentation, and agent interoperability

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Codebase Analysis](#2-codebase-analysis)
3. [Critical Issues](#3-critical-issues)
4. [Improvement Proposals](#4-improvement-proposals)
5. [Architecture Recommendations](#5-architecture-recommendations)
6. [Implementation Roadmap](#6-implementation-roadmap)
7. [Sources & References](#7-sources--references)

---

## 1. Executive Summary

Pathfinder is a structured TDD workflow skill for AI coding agents that uses an expedition metaphor (Scouts write tests, Builders implement). The concept is strong and well-differentiated, but the current implementation has significant gaps between what's documented and what actually exists in the repository. The project is essentially a **documentation-first framework** that lacks the foundational project infrastructure (no `package.json`, no `tsconfig.json`, no `.gitignore`, no CI workflow file) needed to be a functional, installable tool.

This proposal identifies **27 specific improvements** across 6 categories, prioritized by impact and effort.

### Key Findings

| Area | Current State | Rating |
|------|--------------|--------|
| **Concept & Vision** | Excellent expedition metaphor, clear role separation | A |
| **Documentation Quality** | Well-written but references nonexistent files | B- |
| **Project Infrastructure** | Missing `package.json`, `tsconfig.json`, `.gitignore` | F |
| **Test Runner** | Custom runner that ignores Playwright's native capabilities | D |
| **Code Quality** | Anti-patterns in Playwright usage, inconsistent module systems | C- |
| **Agent Interoperability** | Good SKILL.md, but AGENTS.md is too long for agent context | C+ |
| **CI/CD** | Documented but no actual workflow file exists | F |
| **Security** | Credentials guidance is good, but no `.gitignore` to enforce it | D |

---

## 2. Codebase Analysis

### 2.1 What Pathfinder Is

Pathfinder is a **methodology-as-code** project — a TDD workflow packaged as an AI agent skill. It provides:

- A structured 7-phase development process (Survey, Chart, Mark, Scout, Build, Dispatch, Report)
- Role separation between Scout (test writer) and Builder (implementer)
- Visual trail maps using Mermaid diagrams with status markers
- Playwright-based E2E test infrastructure
- Templates for PRs, user journeys, and test files
- Multi-agent coordination protocols

### 2.2 Repository Structure (Actual)

```
Pathfinder/
├── AGENTS.md              (429 lines — agent instructions)
├── SKILL.md               (65 lines — OpenClaw skill definition)
├── README.md              (289 lines — project documentation)
├── LICENSE                (MIT)
├── .env.example           (12 lines — env template)
├── assets/
│   ├── PR_TEMPLATE.md     (75 lines — PR template)
│   ├── USER-JOURNEYS-TEMPLATE.md (131 lines — journey template)
│   ├── example-test.ts    (88 lines — test example)
│   ├── banner.png / .svg  (branding)
│   └── logo.png / .svg    (branding)
├── references/
│   ├── installation.md    (installation guide)
│   ├── tdd-workflow.md    (Scout/Builder protocol)
│   ├── journey-format.md  (trail map spec)
│   ├── component-driven.md (frontend integration)
│   └── ci-integration.md  (CI/CD guide)
└── scripts/
    ├── run-tests.ts       (139 lines — custom test runner)
    ├── setup-auth.ts      (90 lines — auth state setup)
    └── update-coverage.ts (165 lines — coverage sync)
```

**Total code:** ~393 lines of TypeScript across 3 scripts + 1 example
**Total documentation:** ~1,100+ lines of Markdown across 9 files

### 2.3 What's Missing (Referenced But Nonexistent)

| Referenced In | File/Directory Referenced | Exists? |
|---------------|--------------------------|---------|
| README.md | `e2e/test-example.ts` | No |
| README.md | `npm install` / `npm test` | No `package.json` |
| installation.md | `e2e/test-all.ts` | No |
| installation.md | `e2e/scripts/` directory | No |
| ci-integration.md | `.github/workflows/pathfinder.yml` | No |
| ci-integration.md | `docs/test-coverage/USER-JOURNEYS.md` | No |
| AGENTS.md | `.env.local` | No (only `.env.example`) |
| update-coverage.ts | `docs/test-coverage/USER-JOURNEYS.md` | No |
| All scripts | TypeScript compilation | No `tsconfig.json` |
| General | `.gitignore` | No |

---

## 3. Critical Issues

### 3.1 No Project Infrastructure (Severity: Critical)

**Problem:** The repository has no `package.json`, meaning:
- `npm install` (documented in README) will fail
- No dependency declarations for `playwright`, `dotenv`, or `tsx`
- No npm scripts (`test:setup`, `test:e2e`, `test:coverage`)
- No way to declare Node.js version requirements
- The project cannot be installed as a dependency

**Problem:** No `tsconfig.json`, meaning:
- TypeScript compilation behavior is undefined
- IDE support (autocompletion, type checking) won't work reliably
- Path resolution for imports may break across environments

**Problem:** No `.gitignore`, meaning:
- `.env.local` (credentials) could be accidentally committed
- `.auth/state.json` (auth tokens) could be committed
- `node_modules/` could be committed
- `/tmp/test-screenshots/` artifacts could be committed

### 3.2 Custom Test Runner vs. Native Playwright (Severity: High)

**Problem:** The custom `TestRunner` class in `scripts/run-tests.ts` reinvents what Playwright's native `@playwright/test` runner already provides, but worse:

| Feature | Native `@playwright/test` | Custom `TestRunner` |
|---------|--------------------------|---------------------|
| Parallel execution | Built-in workers | Sequential only |
| Auto-waiting | Built-in | Manual checks |
| Test isolation | Per-test browser context | Shared single context |
| Retry on flaky | Configurable retries | None |
| Assertions | `expect()` with rich matchers | Manual `throw new Error()` |
| Reporting | HTML, JSON, JUnit, Allure | Console-only |
| Trace viewer | Built-in for debugging | None |
| CI headless mode | Automatic | Hardcoded `headless: false` |
| Fixtures | Custom fixtures system | None |
| Tagging/filtering | `@tag` annotations | None |
| Config file | `playwright.config.ts` | None |
| Sharding | Built-in for CI | None |

The [Playwright community consensus](https://playwright.dev/) in 2025-2026 is clear: **use the native runner for E2E tests**. The custom runner provides no advantages and sacrifices the entire Playwright ecosystem.

### 3.3 Playwright Anti-Patterns (Severity: High)

**`setup-auth.ts:64`** — Uses `waitForTimeout(1500)`:
```typescript
await page.waitForTimeout(1500); // Anti-pattern: arbitrary wait
```
Playwright's [official documentation](https://playwright.dev/) explicitly discourages `waitForTimeout`. Use `waitForSelector`, `waitForURL`, or `waitForLoadState` instead.

**`setup-auth.ts:69`** — Another `waitForTimeout(3000)`:
```typescript
await page.waitForTimeout(3000); // Anti-pattern: arbitrary wait
```

**`run-tests.ts:58`** — Hardcoded `headless: false`:
```typescript
const browser = await chromium.launch({ headless: false }); // Breaks CI
```
This will fail in any CI environment. Should use `process.env.CI` check or Playwright config.

**`example-test.ts:22-24`** — Manual visibility checks instead of `expect()`:
```typescript
if (!(await header.isVisible({ timeout: 5000 }))) {
  throw new Error('Page header not found');
}
```
Should be:
```typescript
await expect(header).toBeVisible({ timeout: 5000 });
```

### 3.4 Inconsistent Module System (Severity: Medium)

**`assets/example-test.ts:84`** uses ESM:
```typescript
if (import.meta.url === `file://${process.argv[1]}`) {
```

**`references/installation.md:116`** uses CommonJS:
```typescript
if (require.main === module) {
```

**`references/ci-integration.md:69`** uses CommonJS `require`:
```typescript
require('fs').writeFileSync('/tmp/test-results.json', ...);
```

These inconsistencies will cause confusion and runtime errors depending on the target project's module system.

### 3.5 Fragile Markdown Parsing (Severity: Medium)

`update-coverage.ts` uses regex to parse and update Mermaid diagrams and Markdown tables:

```typescript
const mermaidRegex = new RegExp(
  `(\\[.*?)(❌|✅|🔄|⚠️)(\\s*${result.id}\\])`, 'g'
);
```

This is fragile because:
- Unicode emoji matching across platforms is unreliable
- Markdown formatting variations (extra spaces, different line endings) will break the regex
- Mermaid syntax allows many node formats that this regex won't match
- No error handling if the regex fails to match — silently does nothing

---

## 4. Improvement Proposals

### Proposal 1: Add Project Infrastructure (Priority: P0 — Blocking)

**Add `package.json`:**
```json
{
  "name": "pathfinder",
  "version": "0.1.0",
  "description": "TDD workflow using expedition metaphor for AI coding agents",
  "type": "module",
  "scripts": {
    "test:setup": "tsx scripts/setup-auth.ts",
    "test:e2e": "playwright test",
    "test:coverage": "tsx scripts/update-coverage.ts",
    "lint": "eslint scripts/ assets/",
    "format": "prettier --write ."
  },
  "devDependencies": {
    "@playwright/test": "^1.50.0",
    "dotenv": "^16.4.0",
    "tsx": "^4.0.0",
    "typescript": "^5.5.0",
    "eslint": "^9.0.0",
    "prettier": "^3.0.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

**Add `tsconfig.json`:**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist",
    "rootDir": ".",
    "declaration": true
  },
  "include": ["scripts/**/*.ts", "assets/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

**Add `.gitignore`:**
```
node_modules/
dist/
.env.local
.auth/
/tmp/test-screenshots/
*.tsbuildinfo
```

### Proposal 2: Migrate to Native Playwright Test Runner (Priority: P0 — High Impact)

Replace the custom `TestRunner` class with native `@playwright/test` while preserving the Pathfinder expedition metaphor.

**Add `playwright.config.ts`:**
```typescript
import { defineConfig } from '@playwright/test';
import dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    screenshot: 'on',          // Evidence collection built-in
    trace: 'on-first-retry',   // Debugging for flaky tests
    storageState: '.auth/state.json',
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
      dependencies: ['setup'],
    },
  ],
});
```

**Refactored test format** (preserving checkpoint IDs and journey structure):
```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Auth Journey', () => {
  test('AUTH-01: Login redirects to dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/dashboard/);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('AUTH-02: Invalid password shows error', async ({ page }) => {
    // test implementation
  });
});
```

**Benefits gained:**
- Parallel test execution (10-50x faster on large suites)
- Built-in retry for flaky tests
- HTML report with screenshots and traces
- CI/CD-ready out of the box
- Test isolation (each test gets fresh context)
- Rich assertion library (`expect`)
- No custom code to maintain

### Proposal 3: Fix Playwright Anti-Patterns (Priority: P1)

**Replace `waitForTimeout` with explicit waits in `setup-auth.ts`:**

```typescript
// Before (anti-pattern):
await page.waitForTimeout(1500);
await page.locator('input[type="password"]').fill(TEST_PASSWORD);

// After (robust):
await page.locator('input[type="password"]').waitFor({ state: 'visible' });
await page.locator('input[type="password"]').fill(TEST_PASSWORD);
```

**Make headless mode CI-aware in `run-tests.ts`:**

```typescript
// Before:
const browser = await chromium.launch({ headless: false });

// After:
const browser = await chromium.launch({
  headless: process.env.CI === 'true' || process.env.HEADLESS === 'true'
});
```

**Use Playwright assertions in test examples:**

```typescript
// Before (manual throw):
if (!(await header.isVisible({ timeout: 5000 }))) {
  throw new Error('Page header not found');
}

// After (Playwright assertion):
await expect(header).toBeVisible({ timeout: 5000 });
```

### Proposal 4: Add Actual CI/CD Workflow (Priority: P1)

The CI integration guide documents a workflow that doesn't exist. Create `.github/workflows/pathfinder.yml`:

```yaml
name: Pathfinder

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci

      - run: npx playwright install --with-deps chromium

      - name: Run Pathfinder tests
        env:
          CI: 'true'
          TEST_EMAIL: ${{ secrets.TEST_EMAIL }}
          TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
          BASE_URL: http://localhost:3000
        run: npx playwright test

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 14

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: test-results/
          retention-days: 7
```

### Proposal 5: Restructure for Installability (Priority: P1)

The project should be installable via `npm` or copy-paste. Proposed structure:

```
pathfinder/
├── package.json
├── tsconfig.json
├── playwright.config.ts         # NEW: Native Playwright config
├── .gitignore                   # NEW
├── .github/
│   ├── workflows/
│   │   └── pathfinder.yml       # NEW: Actual CI workflow
│   └── PULL_REQUEST_TEMPLATE.md # MOVED from assets/
├── AGENTS.md
├── SKILL.md
├── README.md
├── LICENSE
├── .env.example
├── assets/
│   ├── banner.png / .svg
│   └── logo.png / .svg
├── e2e/                         # NEW: Actual test directory
│   ├── auth.setup.ts            # Auth setup as Playwright project
│   ├── example.spec.ts          # MOVED from assets/example-test.ts
│   └── fixtures/
│       └── pathfinder.ts        # Custom fixture with checkpoint tracking
├── scripts/
│   ├── update-coverage.ts
│   └── init.ts                  # NEW: Project initialization script
├── templates/                   # RENAMED from references + assets templates
│   ├── user-journeys.md
│   ├── test-file.ts
│   └── pr-template.md
└── docs/
    ├── installation.md
    ├── tdd-workflow.md
    ├── journey-format.md
    ├── component-driven.md
    └── ci-integration.md
```

### Proposal 6: Optimize AGENTS.md for Agent Context Windows (Priority: P2)

At 429 lines, AGENTS.md is large for agent context windows. Research from [Addy Osmani's 2026 workflow](https://addyosmani.com/blog/ai-coding-workflow/) and the [Superpowers project](https://yuv.ai/blog/superpowers) shows that agents perform better with concise, structured instructions.

**Proposed changes:**
- Split into `AGENTS.md` (core workflow, ~150 lines max) and `AGENTS-REFERENCE.md` (detailed examples, anti-patterns, templates)
- Add a machine-readable YAML frontmatter section for agent parsers
- Use structured headings that agents can grep for specific phases
- Remove duplicate content between AGENTS.md and reference docs

### Proposal 7: Replace Regex-Based Coverage Sync (Priority: P2)

The current `update-coverage.ts` uses fragile regex to parse Mermaid diagrams and Markdown tables. Replace with a structured data approach:

**Proposal:** Store checkpoint state in a `checkpoints.json` file:
```json
{
  "journeys": {
    "auth": {
      "checkpoints": {
        "AUTH-01": { "status": "pass", "lastRun": "2026-02-10", "description": "Login redirects to dashboard" },
        "AUTH-02": { "status": "fail", "lastRun": "2026-02-10", "description": "Invalid password shows error" }
      }
    }
  }
}
```

Then **generate** the Markdown trail map from this structured data rather than parsing/updating Markdown in place. This eliminates:
- Regex fragility
- Unicode emoji matching issues
- Silent failures when patterns don't match
- Data loss from formatting changes

### Proposal 8: Add an Initialization CLI (Priority: P2)

Create a `scripts/init.ts` that scaffolds Pathfinder into an existing project:

```bash
npx pathfinder init
```

This would:
1. Copy `playwright.config.ts` template
2. Create `e2e/` directory structure
3. Create `docs/test-coverage/USER-JOURNEYS.md` from template
4. Add `.github/workflows/pathfinder.yml`
5. Add `PR_TEMPLATE.md` to `.github/`
6. Update existing `package.json` with required scripts and dependencies
7. Create `.env.example` if not present
8. Update `.gitignore` with Pathfinder exclusions

### Proposal 9: Add Checkpoint Fixture for Playwright (Priority: P2)

Create a custom Playwright fixture that integrates the checkpoint/trail marker system natively:

```typescript
// e2e/fixtures/pathfinder.ts
import { test as base, expect } from '@playwright/test';

type Checkpoint = {
  mark: (id: string, description: string) => void;
  clear: (id: string) => Promise<void>;
};

export const test = base.extend<{ checkpoint: Checkpoint }>({
  checkpoint: async ({ page }, use) => {
    const cleared: string[] = [];

    await use({
      mark(id, description) {
        console.log(`🔄 ${id}: ${description}`);
      },
      async clear(id) {
        console.log(`✅ ${id}: Cleared`);
        cleared.push(id);
      },
    });

    // After test: write results for coverage sync
    // This integrates with update-coverage.ts
  },
});

export { expect };
```

Usage:
```typescript
import { test, expect } from './fixtures/pathfinder';

test('AUTH-01: Login redirects to dashboard', async ({ page, checkpoint }) => {
  checkpoint.mark('AUTH-01', 'Login redirects to dashboard');
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/dashboard/);
  await checkpoint.clear('AUTH-01');
});
```

### Proposal 10: Standardize Module System (Priority: P2)

Commit to ESM throughout. All TypeScript files and documentation examples should use:
- `import` / `export` (not `require`)
- `import.meta.url` for file path resolution (not `__dirname` via workaround)
- `"type": "module"` in `package.json`

Update all code examples in documentation to be consistent.

### Proposal 11: Add Code Quality Tooling (Priority: P3)

**ESLint + Prettier** for consistent code style:
- ESLint flat config with TypeScript plugin
- Prettier for formatting
- Pre-commit hooks via Husky + lint-staged

Consider **Ruff** if any Python scripts are added in the future (per the [multi-language roadmap](https://github.com/srpadrono/Pathfinder/issues)).

### Proposal 12: Security Hardening (Priority: P3)

- Add `.gitignore` immediately (blocks credential commits)
- Add a `SECURITY.md` with vulnerability reporting instructions
- Validate that `AUTH_STATE_PATH` doesn't leak tokens in CI logs
- Add `.env.local` to `.gitignore` template in `init.ts`
- Consider encrypting stored auth state at rest

---

## 5. Architecture Recommendations

### 5.1 Adopt the Playwright Ecosystem Fully

The [2025-2026 consensus](https://playwright.dev/) on Playwright testing is:

> Use the native `@playwright/test` runner. Building a custom runner on top of Playwright's API is an anti-pattern that sacrifices parallelism, isolation, reporting, debugging, and CI integration for no benefit.

Pathfinder should position itself as a **workflow layer on top of Playwright**, not a replacement for Playwright's runner. The expedition metaphor (checkpoints, trail markers, journeys) should be implemented as:
- **Playwright fixtures** (for checkpoint tracking)
- **Playwright projects** (for journey organization)
- **Playwright reporters** (for trail map updates)
- **Playwright config** (for environment management)

### 5.2 Separate Methodology from Tooling

The most valuable part of Pathfinder is the **methodology** (Scout/Builder separation, 7-phase workflow, visual trail maps). The tooling should support the methodology, not compete with established test frameworks.

```
┌─────────────────────────────────────────────────────┐
│                  METHODOLOGY LAYER                  │
│  AGENTS.md, SKILL.md, Workflow Phases, Role Rules   │
├─────────────────────────────────────────────────────┤
│                INTEGRATION LAYER                    │
│  Playwright Fixtures, Reporters, Config Templates   │
├─────────────────────────────────────────────────────┤
│               TOOLING LAYER                         │
│  init CLI, coverage sync, trail map generator       │
├─────────────────────────────────────────────────────┤
│              PLATFORM LAYER                         │
│  @playwright/test, Node.js, TypeScript              │
└─────────────────────────────────────────────────────┘
```

### 5.3 Data-Driven Trail Maps

Move from "documentation that tracks state" to "structured data that generates documentation":

```
checkpoints.json (source of truth)
    ↓
update-coverage.ts (reads test results, updates JSON)
    ↓
generate-map.ts (generates USER-JOURNEYS.md from JSON)
    ↓
USER-JOURNEYS.md (read-only output, committed for visibility)
```

This eliminates the fragile regex parsing of Markdown and provides a reliable API for agent integration.

### 5.4 Multi-Platform Agent Skill Architecture

As the [AI agent skills ecosystem matures](https://github.com/VoltAgent/awesome-agent-skills), Pathfinder should adopt the emerging conventions:

- **SKILL.md**: Machine-readable frontmatter (already present, good)
- **AGENTS.md**: Concise agent instructions with phase-gated sections
- **`.claude/`**: Claude Code-specific configuration (commands, hooks)
- **`.codex/`**: Codex-specific configuration
- Ensure the core methodology is platform-agnostic while platform integration is in separate config directories

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Unblocks everything else)

| # | Task | Files |
|---|------|-------|
| 1.1 | Create `package.json` with all dependencies | `package.json` |
| 1.2 | Create `tsconfig.json` | `tsconfig.json` |
| 1.3 | Create `.gitignore` | `.gitignore` |
| 1.4 | Create `e2e/` directory with example spec | `e2e/example.spec.ts` |
| 1.5 | Add `playwright.config.ts` | `playwright.config.ts` |
| 1.6 | Move `PR_TEMPLATE.md` to `.github/` | `.github/PULL_REQUEST_TEMPLATE.md` |

### Phase 2: Test Runner Migration

| # | Task | Files |
|---|------|-------|
| 2.1 | Convert `setup-auth.ts` to Playwright auth project | `e2e/auth.setup.ts` |
| 2.2 | Convert example test to native Playwright format | `e2e/example.spec.ts` |
| 2.3 | Create Pathfinder custom fixture | `e2e/fixtures/pathfinder.ts` |
| 2.4 | Fix `waitForTimeout` anti-patterns | `scripts/setup-auth.ts` |
| 2.5 | Deprecate custom `TestRunner` class | `scripts/run-tests.ts` |

### Phase 3: Data & Tooling

| # | Task | Files |
|---|------|-------|
| 3.1 | Create `checkpoints.json` schema | `schemas/checkpoints.schema.json` |
| 3.2 | Rewrite `update-coverage.ts` for JSON-based state | `scripts/update-coverage.ts` |
| 3.3 | Create trail map generator from JSON | `scripts/generate-map.ts` |
| 3.4 | Create `init.ts` CLI scaffold script | `scripts/init.ts` |

### Phase 4: CI/CD & Quality

| # | Task | Files |
|---|------|-------|
| 4.1 | Create actual GitHub Actions workflow | `.github/workflows/pathfinder.yml` |
| 4.2 | Add ESLint + Prettier configuration | `.eslintrc.js`, `.prettierrc` |
| 4.3 | Add pre-commit hooks | `.husky/` |
| 4.4 | Standardize all code to ESM | All `.ts` files |

### Phase 5: Agent Optimization

| # | Task | Files |
|---|------|-------|
| 5.1 | Split AGENTS.md into core + reference | `AGENTS.md`, `AGENTS-REFERENCE.md` |
| 5.2 | Add machine-readable phase markers | `AGENTS.md` |
| 5.3 | Add platform-specific agent configs | `.claude/`, `.codex/` |
| 5.4 | Update SKILL.md with expanded metadata | `SKILL.md` |

### Phase 6: Documentation Alignment

| # | Task | Files |
|---|------|-------|
| 6.1 | Fix all broken file references in README | `README.md` |
| 6.2 | Update installation guide for new structure | `docs/installation.md` |
| 6.3 | Update CI guide to match actual workflow | `docs/ci-integration.md` |
| 6.4 | Reconcile all module system examples to ESM | All reference docs |

---

## 7. Sources & References

### Playwright Best Practices
- [Playwright Official Documentation](https://playwright.dev/)
- [Playwright Test Framework Structure: Best Practices for Scalability](https://medium.com/@divyakandpal93/playwright-test-framework-structure-best-practices-for-scalability-eddf6232593d)
- [Guide to Playwright end-to-end testing in 2026](https://www.deviqa.com/blog/guide-to-playwright-end-to-end-testing-in-2025/)
- [The Ultimate Guide to the Playwright Test Runner](https://momentic.ai/resources/the-ultimate-guide-to-the-playwright-test-runner-features-alternatives-best-practices)

### TDD with AI Agents
- [Test-Driven Development with AI — Builder.io](https://www.builder.io/blog/test-driven-development-ai)
- [Stop AI Agents from Writing Spaghetti: Enforcing TDD with Superpowers](https://yuv.ai/blog/superpowers)
- [Agentic TDD — Nizar's Blog](https://nizar.se/agentic-tdd/)
- [AI Agents, Meet Test Driven Development — Latent Space](https://www.latent.space/p/anita-tdd)
- [My LLM Coding Workflow Going Into 2026 — Addy Osmani](https://addyosmani.com/blog/ai-coding-workflow/)

### AI Agent Skills Ecosystem
- [How to Sync AI Skills Across Claude Code, OpenClaw, and Codex](https://dev.to/runkids/how-to-sync-ai-skills-across-claude-code-openclaw-and-codex-in-2-minutes-226e)
- [Awesome Agent Skills Repository](https://github.com/VoltAgent/awesome-agent-skills)
- [OpenAI Skills Catalog: How Codex Adopted the Skills Playbook](https://serenitiesai.com/articles/openai-skills-codex-copied-openclaw-playbook)
- [Pick Your Agent: Use Claude and Codex on Agent HQ — GitHub Blog](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/)

### Project Structure & Tooling
- [Modern Python Project Setup: 2025 Developer's Stack](https://albertsikkema.com/python/development/best-practices/2025/10/31/modern-python-project-setup.html)
- [React Architecture Patterns and Best Practices for 2025](https://www.bacancytechnology.com/blog/react-architecture-patterns-and-best-practices)
- [Create a React + Flask Project in 2025 — Miguel Grinberg](https://blog.miguelgrinberg.com/post/create-a-react-flask-project-in-2025)
- [Structuring Your Project — Hitchhiker's Guide to Python](https://docs.python-guide.org/writing/structure/)

### REST API & Data Patterns
- [Best Practices for REST API Design — Stack Overflow](https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/)
- [API Design Patterns for REST — Stoplight](https://blog.stoplight.io/api-design-patterns-for-rest-web-services)
- [CRUD API Design Recommendations — Stoplight](https://blog.stoplight.io/crud-api-design)

### RPG/Game Design Patterns (Applicable to Structured Data)
- [Design Patterns of Successful Role-Playing Games — Whitson John Kirk III](https://archive.org/details/RPGDesignPatterns91309)
- [D20 RPG Entity Component System — The Liquid Fire](https://theliquidfire.com/2023/04/27/d20-rpg-entity-ecs/)
- [Component Pattern — Game Programming Patterns](https://gameprogrammingpatterns.com/component.html)
- [ECS FAQ — GitHub](https://github.com/SanderMertens/ecs-faq)

### Existing Character Builder/TDD Tools
- [Pathbuilder 2e](https://pathbuilder2e.com/)
- [PCGen — Open Source RPG Character Generator](http://pcgen.org/)
- [Wanderer's Guide](https://wanderersguide.app/)
- [AxleLabs AI — Flask + PostgreSQL NPC Generator](https://github.com/AxleLabs/AxleLabsAI)

---

*This proposal was generated through comprehensive codebase analysis and web research on current best practices as of February 2026.*
