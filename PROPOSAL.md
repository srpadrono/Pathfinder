# Pathfinder Improvement Proposal

**Date:** 2026-02-10
**Author:** Automated Deep Analysis
**Scope:** Architecture, code quality, testing patterns, tooling, documentation, agent interoperability
**Inspiration:** [obra/superpowers](https://github.com/obra/superpowers), [Playwright CLI](https://playwright.dev/docs/test-cli), [@playwright/cli](https://testdino.com/blog/playwright-cli/)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Codebase Analysis](#2-codebase-analysis)
3. [Critical Issues](#3-critical-issues)
4. [Superpowers-Inspired Improvements](#4-superpowers-inspired-improvements)
5. [Playwright CLI Integration](#5-playwright-cli-integration)
6. [Additional Improvement Proposals](#6-additional-improvement-proposals)
7. [Architecture Recommendations](#7-architecture-recommendations)
8. [Implementation Roadmap](#8-implementation-roadmap)
9. [Sources & References](#9-sources--references)

---

## 1. Executive Summary

Pathfinder is a structured TDD workflow skill for AI coding agents that uses an expedition metaphor (Scouts write tests, Builders implement). The concept is strong and well-differentiated, but the current implementation has significant gaps between what's documented and what actually exists in the repository.

This updated proposal incorporates deep inspiration from two sources:

1. **[obra/superpowers](https://github.com/obra/superpowers)** — The leading agentic skills framework (3,787+ stars) that enforces TDD discipline on AI coding agents through composable skills, anti-rationalization tables, SessionStart hooks, slash commands, and subagent-driven development.

2. **[Playwright CLI](https://playwright.dev/docs/test-cli)** and **[@playwright/cli](https://testdino.com/blog/playwright-cli/)** — The native Playwright command-line toolchain including `npx playwright test`, `codegen`, `show-report`, `show-trace`, and the new token-efficient `@playwright/cli` package designed specifically for AI coding agents.

This proposal identifies **38 specific improvements** across 8 categories, prioritized by impact.

### Key Findings

| Area | Current State | Rating | Target |
|------|--------------|--------|--------|
| **Concept & Vision** | Excellent expedition metaphor, clear role separation | A | A+ |
| **Skill Enforcement** | Advisory only — agents can skip phases freely | D | A (Superpowers-style) |
| **Documentation Quality** | Well-written but references nonexistent files | B- | A |
| **Project Infrastructure** | Missing `package.json`, `tsconfig.json`, `.gitignore` | F | A |
| **Test Runner** | Custom runner ignoring Playwright's native capabilities | D | A (Playwright CLI) |
| **Code Quality** | Anti-patterns in Playwright usage, inconsistent modules | C- | B+ |
| **Agent Interoperability** | Good SKILL.md, but AGENTS.md is too long | C+ | A (Superpowers model) |
| **CI/CD** | Documented but no actual workflow file exists | F | A |
| **Security** | Credentials guidance good, no `.gitignore` to enforce | D | B+ |

### Pathfinder vs. Superpowers: Comparison

| Dimension | Pathfinder (Current) | Superpowers | Pathfinder (Proposed) |
|-----------|---------------------|-------------|----------------------|
| **Enforcement model** | Advisory (AGENTS.md) | Mandatory (SessionStart hook + "The Rule") | Mandatory (hooks + enforcement) |
| **Skill composition** | Monolithic AGENTS.md | Composable skills/ directory | Composable skills/ directory |
| **Anti-rationalization** | None | Explicit tables for each rationalization | Expedition-themed anti-rationalization |
| **Slash commands** | None | `/brainstorm`, `/write-plan`, `/execute-plan` | `/survey`, `/scout`, `/build`, `/report` |
| **Subagent coordination** | Documented but not tooled | `subagent-driven-development` skill | Scout/Builder dispatch with review |
| **Hook system** | None | `hooks.json` with SessionStart | `hooks.json` with SessionStart |
| **TDD cycle** | RED-GREEN-REFACTOR (documented) | RED-GREEN-REFACTOR (enforced) | RED-GREEN-REFACTOR (enforced) |
| **Test framework** | Custom TestRunner | Framework-agnostic | Native Playwright CLI |
| **Evidence collection** | Manual screenshots | Verification-before-completion skill | Playwright traces + screenshots |

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
- The project cannot be installed as a dependency

**Problem:** No `tsconfig.json`, meaning:
- TypeScript compilation behavior is undefined
- IDE autocompletion and type checking won't work reliably

**Problem:** No `.gitignore`, meaning:
- `.env.local` (credentials) could be accidentally committed
- `.auth/state.json` (auth tokens) could be committed
- `node_modules/` could be committed

### 3.2 Custom Test Runner vs. Native Playwright (Severity: High)

The custom `TestRunner` class in `scripts/run-tests.ts` reinvents what Playwright's native runner and CLI already provides:

| Feature | Playwright CLI (`npx playwright test`) | Custom `TestRunner` |
|---------|----------------------------------------|---------------------|
| Parallel execution | `--workers=N` flag | Sequential only |
| Auto-waiting | Built-in | Manual checks |
| Test isolation | Per-test browser context | Shared single context |
| Retry on flaky | `--retries=N` flag | None |
| Assertions | `expect()` with rich matchers | Manual `throw new Error()` |
| Reporting | `--reporter=html,json,junit` | Console-only |
| Trace viewer | `npx playwright show-trace` | None |
| Test codegen | `npx playwright codegen` | None |
| CI headless mode | Automatic via `CI` env var | Hardcoded `headless: false` |
| Tag filtering | `--grep @tag` | None |
| Last failed | `--last-failed` flag | None |
| Sharding | `--shard=N/M` | None |

### 3.3 Playwright Anti-Patterns (Severity: High)

**`setup-auth.ts:64`** — `waitForTimeout(1500)` (arbitrary sleep, Playwright anti-pattern)
**`setup-auth.ts:69`** — `waitForTimeout(3000)` (same)
**`run-tests.ts:58`** — `headless: false` hardcoded (breaks CI)
**`example-test.ts:22-24`** — Manual `isVisible()` + `throw` instead of `expect()` assertions

### 3.4 Inconsistent Module System (Severity: Medium)

Mixed ESM (`import.meta.url`) and CommonJS (`require.main === module`) across code and documentation examples.

### 3.5 Fragile Markdown Parsing (Severity: Medium)

`update-coverage.ts` uses regex to parse and update Mermaid diagrams and Markdown tables with Unicode emoji — fragile across platforms and silently fails on format variations.

### 3.6 No Enforcement Mechanism (Severity: High — Superpowers Insight)

**Problem unique to Pathfinder:** The entire workflow is **advisory**. AGENTS.md describes 7 phases, role separation, and "The Iron Law" of TDD — but there is zero enforcement. An agent can read AGENTS.md and skip straight to writing code. There are no:

- SessionStart hooks to auto-inject the workflow
- Slash commands to trigger specific phases
- Anti-rationalization guards to prevent agents from skipping steps
- Verification gates between phases

As [Superpowers demonstrated](https://github.com/obra/superpowers), **agents naturally rationalize skipping skills**. Without explicit enforcement, the workflow degrades to suggestions.

---

## 4. Superpowers-Inspired Improvements

These proposals are directly inspired by patterns from [obra/superpowers](https://github.com/obra/superpowers) (3,787+ stars), adapted to Pathfinder's expedition metaphor.

### Proposal S1: Adopt the Composable Skills Architecture (Priority: P0)

**Superpowers pattern:** Skills are individual Markdown files in a `skills/` directory, each addressing a specific capability. A meta-skill (`using-superpowers`) orchestrates them.

**Pathfinder adaptation:** Decompose the monolithic `AGENTS.md` (429 lines) into composable skills:

```
skills/
├── using-pathfinder/
│   └── SKILL.md              # Meta-skill: "The Rule" + skill routing
├── surveying/
│   └── SKILL.md              # Phase 1: Socratic requirements gathering
├── charting/
│   └── SKILL.md              # Phase 2: Mermaid trail map creation
├── marking/
│   └── SKILL.md              # Phase 3: Checkpoint extraction + edge case matrix
├── scouting/
│   └── SKILL.md              # Phase 4: Writing failing tests (RED)
├── building/
│   └── SKILL.md              # Phase 5: Implementing to pass tests (GREEN)
├── dispatching/
│   └── SKILL.md              # Phase 6: Multi-agent coordination
├── reporting/
│   └── SKILL.md              # Phase 7: PR with evidence
├── test-driven-development/
│   └── SKILL.md              # Core TDD enforcement (RED-GREEN-REFACTOR)
├── verification-before-completion/
│   └── SKILL.md              # Evidence-based verification
└── systematic-debugging/
    └── SKILL.md              # Root-cause debugging methodology
```

**Why this matters:**
- Each skill is small enough for an agent to load on-demand
- Skills can be invoked individually: `pathfinder:scouting`
- New skills can be added without bloating the core workflow
- Skills can be shared, forked, and tested independently

### Proposal S2: Add SessionStart Hook for Automatic Enforcement (Priority: P0)

**Superpowers pattern:** A `hooks.json` file configures a SessionStart hook that injects the meta-skill at the beginning of every Claude Code session. This ensures agents **always** load the workflow — they can't skip it.

**Pathfinder adaptation:** Create `hooks/hooks.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "command": "cat skills/using-pathfinder/SKILL.md"
      }
    ]
  }
}
```

And create the meta-skill `skills/using-pathfinder/SKILL.md`:

```markdown
---
name: using-pathfinder
description: >
  Meta-skill that bootstraps the Pathfinder expedition workflow.
  Automatically loaded at session start.
---

# Using Pathfinder

## THE RULE

If there is even a 1% chance a Pathfinder skill applies to your current task,
you MUST invoke it. This is not optional. This is not a suggestion.

## Skill Routing

| Trigger | Skill | When |
|---------|-------|------|
| New feature, user story, requirement | `pathfinder:surveying` | Before ANY code or tests |
| Need a visual journey/flow | `pathfinder:charting` | After survey approved |
| Defining test cases or checkpoints | `pathfinder:marking` | After map charted |
| Writing E2E or integration tests | `pathfinder:scouting` | After checkpoints marked |
| Implementing features | `pathfinder:building` | After ALL tests written |
| Coordinating scout/builder agents | `pathfinder:dispatching` | Multi-agent mode |
| Creating PR or expedition report | `pathfinder:reporting` | After all tests pass |
| Something is broken/failing | `pathfinder:systematic-debugging` | Any time |

## Process Skills Come First

When multiple skills apply, process skills (surveying, scouting) ALWAYS come
before implementation skills (building). "Build X" triggers surveying first.

## Enforcement

- Cannot skip Survey phase for new features
- Cannot write production code without a failing test
- Cannot mark a checkpoint as cleared without evidence
- Cannot create a PR without all checkpoints passing
```

### Proposal S3: Add Slash Commands for Phase Activation (Priority: P1)

**Superpowers pattern:** `/brainstorm`, `/write-plan`, `/execute-plan` are slash commands that activate specific workflow phases. Commands are defined as Markdown files in `commands/`.

**Pathfinder adaptation:** Create expedition-themed slash commands:

```
commands/
├── survey.md       # /survey — Start requirements gathering
├── scout.md        # /scout — Enter Scout mode (write tests)
├── build.md        # /build — Enter Builder mode (implement)
└── report.md       # /report — Generate expedition report
```

**`commands/survey.md`:**
```markdown
---
disable-model-invocation: true
---

Invoke the `pathfinder:surveying` skill to begin terrain survey.

Read the project context, then ask clarifying questions ONE AT A TIME
using multiple choice where possible. Focus on: purpose, constraints,
success criteria, edge cases, error states.

After surveying, propose 2-3 approaches with trade-offs.
```

**`commands/scout.md`:**
```markdown
---
disable-model-invocation: true
---

Invoke the `pathfinder:scouting` skill.

PREREQUISITE: A charted trail map must exist in USER-JOURNEYS.md.
If no map exists, invoke `pathfinder:surveying` first.

Write failing tests for ALL checkpoints before any implementation.
Use Playwright CLI:
- Generate test scaffolding: `npx playwright codegen <url>`
- Run tests to verify RED: `npx playwright test --grep <checkpoint-id>`
- Verify failure is correct (missing feature, not typo)

After all tests written, update markers: ❌ → 🔄
Commit: "Scout: Mark trail for FEAT-01 through FEAT-XX"
```

**`commands/build.md`:**
```markdown
---
disable-model-invocation: true
---

Invoke the `pathfinder:building` skill.

PREREQUISITE: All checkpoint tests must exist and FAIL (🔄 status).
If tests don't exist, invoke `pathfinder:scouting` first.

Implement minimal code to pass each test, ONE AT A TIME.
Use Playwright CLI:
- Run single checkpoint: `npx playwright test --grep "FEAT-01"`
- Run all journey tests: `npx playwright test e2e/<journey>.spec.ts`
- Debug failures: `npx playwright test --debug`
- View trace on retry: `npx playwright show-trace`

After each checkpoint clears, update markers: 🔄 → ✅
Commit: "Builder: Clear FEAT-01"
```

**`commands/report.md`:**
```markdown
---
disable-model-invocation: true
---

Invoke the `pathfinder:reporting` skill.

PREREQUISITE: All checkpoints must be ✅.
If any checkpoint is not cleared, invoke `pathfinder:building` first.

Generate expedition report:
1. Run full test suite: `npx playwright test`
2. Generate HTML report: `npx playwright show-report`
3. Collect evidence screenshots from `test-results/`
4. Create PR using assets/PR_TEMPLATE.md
```

### Proposal S4: Add Anti-Rationalization Tables (Priority: P1)

**Superpowers pattern:** Each skill includes explicit counters for common rationalizations that agents use to skip the skill. These are discovered through TDD testing of the skills themselves (run scenario WITHOUT skill, observe failure, add counter).

**Pathfinder adaptation for the TDD skill (`skills/test-driven-development/SKILL.md`):**

```markdown
## Anti-Rationalization Guide

Agents WILL try to skip TDD. These are the most common rationalizations
and why they are wrong:

| Rationalization | Why It's Wrong | What To Do |
|----------------|---------------|-----------|
| "This is too simple to test" | Simple code breaks most often. A 1-line regex can have 10 edge cases. | Write the test. It'll take 30 seconds. |
| "I'll write tests after" | Tests-after verify YOUR implementation. Tests-first verify THE REQUIREMENT. Tests-after are biased. | Delete the code. Write the test first. |
| "I already manually verified it works" | Manual testing is ad-hoc, non-systematic, and unreproducible. | Not evidence. Write the test. |
| "Deleting working code is wasteful" | Sunk cost fallacy. Unverified code is technical debt, not an asset. | Delete it. The test-first version will be better. |
| "The test passed immediately" | Then it doesn't test new behavior. It tests existing behavior or is wrong. | Rewrite to test the NEW requirement. |
| "I just need to fix this one thing quickly" | Scope creep starts here. One quick fix becomes three. | Stop. Survey the terrain first. |
| "The tests are in my head" | Invisible tests don't catch regressions, can't be automated, and die with your session. | Write them down. In code. Now. |
| "I'll keep the code as reference while writing tests" | You'll unconsciously write tests that validate your implementation instead of the requirement. | Close the file. Delete the code. Fresh start. |

### Red Flags That TDD Has Been Abandoned

If ANY of these occur, STOP and restart from Scout phase:

- You wrote production code before a test
- A test passed on first run (without implementation)
- You modified a test to make it pass (instead of modifying production code)
- You skipped a checkpoint because "it's obvious"
- You're writing tests and code in the same commit
- You rationalized "just this once"
```

### Proposal S5: Add Two-Stage Review for Dispatch Phase (Priority: P1)

**Superpowers pattern:** After each subagent task, a two-stage review runs:
1. **Spec Compliance Review** — Does implementation match checkpoint requirements exactly?
2. **Code Quality Review** — Only runs after spec passes; reviews for clean code.

**Pathfinder adaptation for `skills/dispatching/SKILL.md`:**

```markdown
## Two-Stage Expedition Review

After each Builder completes a checkpoint:

### Stage 1: Trail Compliance Review
A reviewer (separate agent or fresh context) verifies:
- [ ] Implementation matches the checkpoint description exactly
- [ ] No extra features beyond what the checkpoint requires (YAGNI)
- [ ] Test was written BEFORE implementation (check git log timestamps)
- [ ] Screenshot evidence matches expected behavior
- [ ] Marker correctly updated (🔄 → ✅)

If trail compliance fails → Builder fixes → Re-review Stage 1.

### Stage 2: Code Quality Review
Only runs after Stage 1 passes:
- [ ] Minimal code — simplest solution that passes the test
- [ ] No console errors or warnings
- [ ] No hardcoded values that should be configurable
- [ ] Error handling for the specific checkpoint's edge cases
- [ ] Code matches project conventions

If quality fails → Builder fixes → Re-review Stage 2 only.

### Review Is a Loop
Reviews repeat until both stages pass. No exceptions.
```

### Proposal S6: Add Verification-Before-Completion Skill (Priority: P1)

**Superpowers pattern:** Agents must provide concrete evidence before claiming a task is complete. No self-certifying. "Evidence over claims."

**Pathfinder adaptation (`skills/verification-before-completion/SKILL.md`):**

```markdown
# Verification Before Completion

## The Rule
NEVER claim a checkpoint is cleared without evidence.
NEVER claim all tests pass without running them.
NEVER mark 🔄 → ✅ without a passing test run.

## Required Evidence Per Checkpoint

| Claim | Required Evidence |
|-------|------------------|
| "Test is written" | Show the test code + show it FAILS with expected message |
| "Checkpoint cleared" | Show `npx playwright test --grep "FEAT-XX"` output with PASS |
| "All tests pass" | Show `npx playwright test` full output with 0 failures |
| "No regressions" | Show full suite run, not just the new test |
| "Trail map updated" | Show the diff of USER-JOURNEYS.md with updated markers |
| "PR ready" | Show pre-review checklist with all items checked |

## Verification Commands (Playwright CLI)

```bash
# Verify single checkpoint
npx playwright test --grep "AUTH-01" --reporter=list

# Verify entire journey
npx playwright test e2e/auth.spec.ts --reporter=list

# Verify all (no regressions)
npx playwright test --reporter=list

# Generate HTML evidence report
npx playwright test --reporter=html
npx playwright show-report

# Inspect failure trace
npx playwright show-trace test-results/<test>/trace.zip
```

## Anti-Rationalization

| Rationalization | Counter |
|----------------|---------|
| "I'm confident it works" | Confidence is not evidence. Run the test. |
| "I tested it manually" | Manual is not automated. Run `npx playwright test`. |
| "The previous test was similar" | Similar is not identical. Run THIS test. |
| "It's just a small change" | Small changes cause big regressions. Run the suite. |
```

### Proposal S7: TDD-Test the Skills Themselves (Priority: P2)

**Superpowers pattern:** Skills are created using TDD methodology applied to documentation:
- **RED:** Run scenario WITHOUT skill, observe agent failures and rationalizations
- **GREEN:** Write skill addressing specific failures
- **REFACTOR:** Close loopholes by adding explicit counters for each rationalization

**Pathfinder adaptation:** Create `skills/writing-skills/SKILL.md` with a process for developing new Pathfinder skills:

```markdown
# Writing Pathfinder Skills

## Skills Are TDD-Tested Documentation

### RED Phase — Observe the Failure
1. Give an agent a task WITHOUT the skill loaded
2. Document what goes wrong:
   - Did it skip the survey?
   - Did it write code before tests?
   - Did it claim completion without evidence?
   - What rationalizations did it use?

### GREEN Phase — Write the Skill
1. Address each observed failure explicitly
2. Add anti-rationalization counters for each excuse
3. Add verification requirements for each claim

### REFACTOR Phase — Close Loopholes
1. Run the scenario again WITH the skill
2. If the agent finds a new way to skip: add a counter
3. If the skill is too verbose: simplify without losing enforcement
4. If agents ignore a section: restructure for scannability
```

### Proposal S8: Add Fresh Context Principle for Subagents (Priority: P2)

**Superpowers pattern:** Each dispatched subagent starts with fresh context. No pollution from previous tasks. Tasks include everything the subagent needs — exact file paths, complete code snippets, verification steps.

**Pathfinder adaptation for Scout/Builder dispatch:**

```markdown
## Fresh Context Dispatch

When spawning a Scout or Builder subagent, provide COMPLETE context:

### Scout Dispatch Template
```
You are a SCOUT for the Pathfinder expedition workflow.

YOUR TERRITORY: e2e/ and USER-JOURNEYS.md ONLY.
FORBIDDEN: Do NOT modify src/ or any implementation code.

TASK: Write failing tests for checkpoints FEAT-01 through FEAT-05.

TRAIL MAP: [paste relevant section of USER-JOURNEYS.md]

CHECKPOINT DETAILS:
- FEAT-01: [description + acceptance criteria]
- FEAT-02: [description + acceptance criteria]

TEST FILE: e2e/feature.spec.ts
TEST COMMAND: npx playwright test e2e/feature.spec.ts
EXPECTED RESULT: All tests FAIL (feature not implemented yet)

WHEN DONE:
1. Commit: "Scout: Mark trail for FEAT-01 through FEAT-05"
2. Update USER-JOURNEYS.md markers: ❌ → 🔄
3. Report: List all checkpoints with their test descriptions
```

### Builder Dispatch Template
```
You are a BUILDER for the Pathfinder expedition workflow.

YOUR TERRITORY: src/ and implementation code ONLY.
FORBIDDEN: Do NOT modify test assertions in e2e/.

TASK: Clear trail for checkpoints FEAT-01 through FEAT-05.

TRAIL MAP: [paste relevant section of USER-JOURNEYS.md]
TESTS: e2e/feature.spec.ts

FOR EACH CHECKPOINT:
1. Run: npx playwright test --grep "FEAT-XX"
2. Verify it FAILS (expected)
3. Write minimal code to pass
4. Run: npx playwright test --grep "FEAT-XX"
5. Verify it PASSES
6. Commit: "Builder: Clear FEAT-XX"
7. Update marker: 🔄 → ✅

WHEN DONE:
1. Run full suite: npx playwright test
2. Verify 0 failures
3. Report: List all checkpoints with pass/fail status and duration
```
```

---

## 5. Playwright CLI Integration

These proposals leverage the full Playwright CLI toolchain to replace the custom `TestRunner` and provide a professional, production-grade testing experience.

### Proposal P1: Migrate to Native Playwright Test Runner (Priority: P0)

Replace the custom `TestRunner` class with native `@playwright/test` and the `npx playwright` CLI.

**Add `playwright.config.ts`:**
```typescript
import { defineConfig, devices } from '@playwright/test';
import dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    screenshot: 'on',
    trace: 'on-first-retry',
    video: 'on-first-retry',
  },
  projects: [
    // Auth setup runs first
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    // All journeys depend on auth
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: '.auth/state.json' },
      dependencies: ['setup'],
    },
    // Optional: cross-browser
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'], storageState: '.auth/state.json' },
      dependencies: ['setup'],
    },
  ],
});
```

### Proposal P2: Leverage Playwright CLI Commands Throughout the Workflow (Priority: P0)

Map every expedition phase to specific Playwright CLI commands:

| Expedition Phase | Playwright CLI Command | Purpose |
|-----------------|----------------------|---------|
| **Survey** | `npx playwright codegen <url>` | Generate test scaffolding by recording interactions |
| **Scout (write tests)** | `npx playwright test --grep "FEAT-XX" --reporter=list` | Verify tests FAIL (RED) |
| **Build (implement)** | `npx playwright test --grep "FEAT-XX"` | Verify tests PASS (GREEN) |
| **Build (debug)** | `npx playwright test --debug` | Step-through debugging in headed browser |
| **Build (trace)** | `npx playwright show-trace test-results/<test>/trace.zip` | Inspect failure traces visually |
| **Report** | `npx playwright test --reporter=html` | Generate evidence report |
| **Report (view)** | `npx playwright show-report` | View HTML report in browser |
| **CI (parallel)** | `npx playwright test --shard=1/4` | Shard tests across CI workers |
| **CI (retry flaky)** | `npx playwright test --retries=2` | Automatically retry flaky tests |
| **CI (last failed)** | `npx playwright test --last-failed` | Re-run only previously failed tests |

**Update AGENTS.md and skill files to reference these CLI commands instead of the custom runner.**

### Proposal P3: Use `npx playwright codegen` for Scout Phase (Priority: P1)

The `codegen` command records browser interactions and generates test code — perfect for the Scout phase:

```bash
# Scout records the happy path interaction
npx playwright codegen http://localhost:3000/feature

# With saved auth state (skip login)
npx playwright codegen --load-storage=.auth/state.json http://localhost:3000/feature

# With specific viewport (mobile testing)
npx playwright codegen --viewport-size="375,812" http://localhost:3000/feature

# Save auth state for reuse
npx playwright codegen --save-storage=.auth/state.json http://localhost:3000/auth/login
```

This replaces the custom `setup-auth.ts` with a standard Playwright pattern:
- `npx playwright codegen --save-storage` for recording auth state
- `npx playwright codegen --load-storage` for generating authenticated tests

**Add to `skills/scouting/SKILL.md`:**

```markdown
## Codegen-Assisted Scouting

For complex UI flows, use Playwright's codegen to record interactions:

1. Start recording: `npx playwright codegen --load-storage=.auth/state.json <url>`
2. Perform the user journey in the opened browser
3. Copy the generated test code
4. Refactor into checkpoint format with proper assertions
5. Add edge case tests that codegen can't capture (errors, empty states)

Codegen captures the HAPPY PATH. The Scout must ALSO write:
- Error state tests (mock API failures)
- Empty state tests (mock empty responses)
- Edge case tests (boundary values, race conditions)
- Validation tests (invalid inputs)
```

### Proposal P4: Convert Auth Setup to Playwright Project (Priority: P1)

Replace custom `scripts/setup-auth.ts` with Playwright's native auth setup pattern:

**`e2e/auth.setup.ts`:**
```typescript
import { test as setup, expect } from '@playwright/test';

const AUTH_FILE = '.auth/state.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/auth/login');

  // Fill email — wait for element, not arbitrary timeout
  const emailInput = page.locator('input[type="email"], input[inputmode="email"]').first();
  await emailInput.fill(process.env.TEST_EMAIL!);
  await page.locator('button[type="submit"]').first().click();

  // Fill password — auto-wait, no waitForTimeout
  await page.locator('input[type="password"]').fill(process.env.TEST_PASSWORD!);
  await page.locator('button[type="submit"]').first().click();

  // Wait for redirect to app
  await page.waitForURL(/localhost/);
  await page.waitForLoadState('networkidle');

  // Save state
  await page.context().storageState({ path: AUTH_FILE });
});
```

**Benefits over current `setup-auth.ts`:**
- No `waitForTimeout` anti-patterns
- Uses Playwright's auto-waiting
- Runs as a Playwright project dependency (automatic ordering)
- Reuses auth state across all test projects via `storageState`
- CLI-integrated: `npx playwright test --project=setup`

### Proposal P5: Add `@playwright/cli` for Token-Efficient Agent Workflows (Priority: P2)

The new [`@playwright/cli`](https://testdino.com/blog/playwright-cli/) package is designed specifically for AI coding agents. While `npx playwright` is built for human debugging, `@playwright/cli` is optimized for:

- **Token efficiency:** Concise, purpose-built commands avoid loading large tool schemas and verbose accessibility trees into model context
- **Structured output:** Results formatted for programmatic consumption
- **Agent-friendly:** Designed for automated workflows, not interactive use

**Integration into Pathfinder skills:**

```markdown
## AI Agent Testing Commands

When running as an AI coding agent, prefer `@playwright/cli` for token efficiency:

### Install
npm install --save-dev @playwright/cli

### Usage
# Token-efficient test execution
playwright-cli test --grep "AUTH-01"

# Structured results for programmatic parsing
playwright-cli test --reporter=json

# Browser automation for verification
playwright-cli navigate http://localhost:3000/dashboard
playwright-cli screenshot --path evidence/dashboard.png
playwright-cli assert-visible '[data-testid="well-grid"]'
```

**When to use which:**

| Command | Use When |
|---------|----------|
| `npx playwright test` | Human developer running tests locally |
| `npx playwright codegen` | Human or agent generating test scaffolding |
| `npx playwright show-report` | Human reviewing test results |
| `npx playwright show-trace` | Human debugging failures |
| `@playwright/cli` | AI agent running tests (token-efficient) |

### Proposal P6: Playwright Custom Reporter for Trail Map Updates (Priority: P2)

Instead of regex-parsing Markdown, create a custom Playwright reporter that automatically updates trail maps:

**`e2e/reporters/pathfinder-reporter.ts`:**
```typescript
import type { Reporter, TestCase, TestResult, FullResult } from '@playwright/test/reporter';
import * as fs from 'fs';

class PathfinderReporter implements Reporter {
  private results: Map<string, 'pass' | 'fail' | 'skip'> = new Map();

  onTestEnd(test: TestCase, result: TestResult) {
    // Extract checkpoint ID from test title (e.g., "AUTH-01: Login redirects")
    const match = test.title.match(/^([A-Z]+-\d+):/);
    if (match) {
      this.results.set(match[1], result.status === 'passed' ? 'pass' : 'fail');
    }
  }

  onEnd(result: FullResult) {
    // Write structured results to JSON
    const output = {
      timestamp: new Date().toISOString(),
      status: result.status,
      checkpoints: Object.fromEntries(this.results),
    };
    fs.writeFileSync('test-results/checkpoints.json', JSON.stringify(output, null, 2));

    // Log trail map update commands
    console.log('\n🗺️  Trail Map Updates:');
    for (const [id, status] of this.results) {
      const marker = status === 'pass' ? '✅' : '❌';
      console.log(`   ${marker} ${id}`);
    }
  }
}

export default PathfinderReporter;
```

**Register in `playwright.config.ts`:**
```typescript
reporter: [
  ['list'],
  ['html', { open: 'never' }],
  ['./e2e/reporters/pathfinder-reporter.ts'],
],
```

**Then `scripts/update-coverage.ts` reads `test-results/checkpoints.json` instead of parsing Markdown.**

### Proposal P7: Add Pathfinder Checkpoint Fixture (Priority: P2)

Custom Playwright fixture that integrates the checkpoint/trail marker system natively:

**`e2e/fixtures/pathfinder.ts`:**
```typescript
import { test as base, expect } from '@playwright/test';
import * as fs from 'fs';

interface TrailMarker {
  id: string;
  description: string;
  status: 'uncharted' | 'scouted' | 'cleared' | 'unstable' | 'skipped';
}

type PathfinderFixtures = {
  checkpoint: {
    mark: (id: string, description: string) => void;
    clear: (id: string) => void;
    getMarkers: () => TrailMarker[];
  };
};

export const test = base.extend<PathfinderFixtures>({
  checkpoint: async ({}, use, testInfo) => {
    const markers: TrailMarker[] = [];

    await use({
      mark(id: string, description: string) {
        markers.push({ id, description, status: 'scouted' });
        testInfo.annotations.push({ type: 'checkpoint', description: `${id}: ${description}` });
      },
      clear(id: string) {
        const marker = markers.find(m => m.id === id);
        if (marker) marker.status = 'cleared';
      },
      getMarkers() {
        return [...markers];
      },
    });

    // After test: attach markers as test metadata
    const resultFile = `test-results/markers-${testInfo.testId}.json`;
    fs.mkdirSync('test-results', { recursive: true });
    fs.writeFileSync(resultFile, JSON.stringify(markers, null, 2));
  },
});

export { expect };
```

**Usage in tests:**
```typescript
import { test, expect } from '../fixtures/pathfinder';

test.describe('Auth Journey', () => {
  test('AUTH-01: Login redirects to dashboard', async ({ page, checkpoint }) => {
    checkpoint.mark('AUTH-01', 'Login redirects to dashboard');

    await page.goto('/dashboard');
    await expect(page).toHaveURL(/dashboard/);
    await expect(page.locator('h1')).toBeVisible();

    checkpoint.clear('AUTH-01');
  });

  test('AUTH-02: Invalid password shows error', async ({ page, checkpoint }) => {
    checkpoint.mark('AUTH-02', 'Invalid password shows error');

    await page.goto('/auth/login');
    // ... test implementation using proper expect() assertions ...

    checkpoint.clear('AUTH-02');
  });
});
```

---

## 6. Additional Improvement Proposals

### Proposal A1: Add Project Infrastructure (Priority: P0 — Blocking)

**`package.json`:**
```json
{
  "name": "pathfinder",
  "version": "0.1.0",
  "description": "TDD workflow using expedition metaphor for AI coding agents",
  "type": "module",
  "scripts": {
    "test": "playwright test",
    "test:setup": "playwright test --project=setup",
    "test:headed": "playwright test --headed",
    "test:debug": "playwright test --debug",
    "test:report": "playwright show-report",
    "test:codegen": "playwright codegen --load-storage=.auth/state.json",
    "test:coverage": "tsx scripts/update-coverage.ts",
    "test:trace": "playwright show-trace",
    "lint": "eslint scripts/ e2e/",
    "format": "prettier --write ."
  },
  "devDependencies": {
    "@playwright/test": "^1.50.0",
    "dotenv": "^16.4.0",
    "tsx": "^4.0.0",
    "typescript": "^5.5.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

**`tsconfig.json`:**
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
    "rootDir": "."
  },
  "include": ["scripts/**/*.ts", "e2e/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

**`.gitignore`:**
```
node_modules/
dist/
.env.local
.auth/
test-results/
playwright-report/
blob-report/
*.tsbuildinfo
```

### Proposal A2: Add Actual CI/CD Workflow (Priority: P1)

Create `.github/workflows/pathfinder.yml`:

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
    timeout-minutes: 15
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

### Proposal A3: Replace Regex-Based Coverage with JSON Pipeline (Priority: P2)

```
npx playwright test                    # Produces test-results/results.json
    ↓
PathfinderReporter                     # Produces test-results/checkpoints.json
    ↓
npx tsx scripts/update-coverage.ts     # Reads checkpoints.json, updates JSON state
    ↓
npx tsx scripts/generate-map.ts        # Generates USER-JOURNEYS.md from JSON
```

### Proposal A4: Add Initialization CLI (Priority: P2)

```bash
npx pathfinder init
```

Scaffolds:
1. `playwright.config.ts`
2. `e2e/` directory with auth setup and example spec
3. `e2e/fixtures/pathfinder.ts`
4. `e2e/reporters/pathfinder-reporter.ts`
5. `docs/test-coverage/USER-JOURNEYS.md`
6. `.github/workflows/pathfinder.yml`
7. `.github/PULL_REQUEST_TEMPLATE.md`
8. `skills/` directory with core skills
9. `hooks/hooks.json`
10. `commands/` directory with slash commands
11. Updates `.gitignore`
12. Updates `package.json` with scripts and dependencies

### Proposal A5: Standardize Module System to ESM (Priority: P2)

All TypeScript files and documentation examples should use ESM consistently:
- `import` / `export` (not `require`)
- `import.meta.url` for file path resolution
- `"type": "module"` in `package.json`

---

## 7. Architecture Recommendations

### 7.1 Proposed Repository Structure

```
pathfinder/
├── package.json                        # NEW
├── tsconfig.json                       # NEW
├── playwright.config.ts                # NEW: Native Playwright config
├── .gitignore                          # NEW
│
├── skills/                             # NEW: Superpowers-style composable skills
│   ├── using-pathfinder/
│   │   └── SKILL.md                    # Meta-skill: routing + enforcement
│   ├── surveying/
│   │   └── SKILL.md                    # Phase 1: Requirements gathering
│   ├── charting/
│   │   └── SKILL.md                    # Phase 2: Trail map creation
│   ├── marking/
│   │   └── SKILL.md                    # Phase 3: Checkpoint extraction
│   ├── scouting/
│   │   └── SKILL.md                    # Phase 4: Writing failing tests
│   ├── building/
│   │   └── SKILL.md                    # Phase 5: Implementation
│   ├── dispatching/
│   │   └── SKILL.md                    # Phase 6: Multi-agent coordination
│   ├── reporting/
│   │   └── SKILL.md                    # Phase 7: PR with evidence
│   ├── test-driven-development/
│   │   └── SKILL.md                    # Core TDD enforcement
│   ├── verification-before-completion/
│   │   └── SKILL.md                    # Evidence-based verification
│   ├── systematic-debugging/
│   │   └── SKILL.md                    # Root-cause debugging
│   └── writing-skills/
│       └── SKILL.md                    # Meta: how to write new skills
│
├── hooks/                              # NEW: Superpowers-style hooks
│   └── hooks.json                      # SessionStart hook config
│
├── commands/                           # NEW: Slash commands
│   ├── survey.md                       # /survey
│   ├── scout.md                        # /scout
│   ├── build.md                        # /build
│   └── report.md                       # /report
│
├── e2e/                                # NEW: Actual test directory
│   ├── auth.setup.ts                   # Playwright auth project
│   ├── example.spec.ts                 # Example test using checkpoint fixture
│   ├── fixtures/
│   │   └── pathfinder.ts              # Checkpoint tracking fixture
│   └── reporters/
│       └── pathfinder-reporter.ts     # Trail map update reporter
│
├── scripts/
│   ├── update-coverage.ts             # REWRITTEN: JSON-based state
│   ├── generate-map.ts                # NEW: Generate USER-JOURNEYS.md from JSON
│   └── init.ts                        # NEW: Project scaffolding CLI
│
├── templates/                          # REORGANIZED
│   ├── user-journeys.md               # Trail map template
│   ├── test-file.ts                   # Test file template
│   └── pr-template.md                 # PR template
│
├── .github/                            # NEW
│   ├── workflows/
│   │   └── pathfinder.yml             # Actual CI workflow
│   └── PULL_REQUEST_TEMPLATE.md       # Moved from assets/
│
├── AGENTS.md                          # SLIMMED: Points to skills/
├── SKILL.md                           # OpenClaw skill definition
├── README.md                          # UPDATED: Accurate file references
├── LICENSE
├── .env.example
├── assets/
│   ├── banner.png / .svg
│   └── logo.png / .svg
└── docs/
    ├── installation.md
    ├── tdd-workflow.md
    ├── journey-format.md
    ├── component-driven.md
    └── ci-integration.md
```

### 7.2 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ENFORCEMENT LAYER                          │
│  hooks/hooks.json (SessionStart) → skills/using-pathfinder/     │
│  Anti-rationalization tables, "The Rule", verification gates    │
├─────────────────────────────────────────────────────────────────┤
│                      METHODOLOGY LAYER                          │
│  skills/ (composable), commands/ (slash), AGENTS.md (summary)   │
│  Survey → Chart → Mark → Scout → Build → Dispatch → Report     │
├─────────────────────────────────────────────────────────────────┤
│                      INTEGRATION LAYER                          │
│  e2e/fixtures/pathfinder.ts (checkpoint fixture)                │
│  e2e/reporters/pathfinder-reporter.ts (trail map reporter)      │
│  playwright.config.ts (projects, auth, evidence)                │
├─────────────────────────────────────────────────────────────────┤
│                      TOOLING LAYER                              │
│  scripts/init.ts, update-coverage.ts, generate-map.ts           │
│  templates/ (user-journeys, test files, PR template)            │
├─────────────────────────────────────────────────────────────────┤
│                      PLATFORM LAYER                             │
│  npx playwright test/codegen/show-report/show-trace             │
│  @playwright/cli (token-efficient for AI agents)                │
│  @playwright/test, Node.js, TypeScript                          │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 Data Flow: From Tests to Trail Maps

```
npx playwright test
    │
    ├── [Built-in] Screenshots → test-results/screenshots/
    ├── [Built-in] Traces → test-results/traces/
    ├── [Built-in] HTML Report → playwright-report/
    ├── [Built-in] JSON Results → test-results/results.json
    │
    └── [Custom] PathfinderReporter → test-results/checkpoints.json
                                          │
                                    update-coverage.ts
                                          │
                                    checkpoints.json (source of truth)
                                          │
                                    generate-map.ts
                                          │
                                    USER-JOURNEYS.md (generated, committed)
```

---

## 8. Implementation Roadmap

### Phase 1: Foundation (P0 — Unblocks everything)

| # | Task | Inspiration |
|---|------|-------------|
| 1.1 | Create `package.json` with Playwright CLI scripts | — |
| 1.2 | Create `tsconfig.json` | — |
| 1.3 | Create `.gitignore` | — |
| 1.4 | Create `playwright.config.ts` with projects | Playwright CLI |
| 1.5 | Create `e2e/` directory with auth setup + example spec | Playwright CLI |
| 1.6 | Create `e2e/auth.setup.ts` (replaces `setup-auth.ts`) | `npx playwright codegen --save-storage` |

### Phase 2: Skills Architecture (P0 — Superpowers-inspired)

| # | Task | Superpowers Pattern |
|---|------|---------------------|
| 2.1 | Create `skills/` directory structure | Composable skills |
| 2.2 | Create `skills/using-pathfinder/SKILL.md` meta-skill | `using-superpowers` meta-skill |
| 2.3 | Decompose AGENTS.md into individual skills | Skill separation |
| 2.4 | Add anti-rationalization tables to each skill | Anti-rationalization design |
| 2.5 | Create `hooks/hooks.json` with SessionStart | SessionStart hook |
| 2.6 | Create `commands/` slash commands | `/brainstorm`, `/write-plan`, `/execute-plan` |

### Phase 3: Playwright Integration (P1)

| # | Task | Playwright CLI Feature |
|---|------|----------------------|
| 3.1 | Create checkpoint fixture | `test.extend` fixtures |
| 3.2 | Create Pathfinder custom reporter | Custom reporters API |
| 3.3 | Update all test examples to use `expect()` assertions | `@playwright/test` assertions |
| 3.4 | Add codegen workflow to scouting skill | `npx playwright codegen` |
| 3.5 | Add debug/trace workflow to building skill | `npx playwright test --debug`, `show-trace` |
| 3.6 | Deprecate custom `TestRunner` class | Native `npx playwright test` |

### Phase 4: Enforcement & Verification (P1 — Superpowers-inspired)

| # | Task | Superpowers Pattern |
|---|------|---------------------|
| 4.1 | Create `skills/verification-before-completion/SKILL.md` | Verification skill |
| 4.2 | Create `skills/systematic-debugging/SKILL.md` | Systematic debugging |
| 4.3 | Add two-stage review to `skills/dispatching/SKILL.md` | Two-stage review |
| 4.4 | Add fresh context templates for Scout/Builder dispatch | Fresh context principle |
| 4.5 | Create `skills/writing-skills/SKILL.md` | TDD-tested skills |

### Phase 5: Data Pipeline (P2)

| # | Task |
|---|------|
| 5.1 | Rewrite `update-coverage.ts` for JSON-based state |
| 5.2 | Create `generate-map.ts` for Markdown generation |
| 5.3 | Create `checkpoints.json` schema |
| 5.4 | Create `scripts/init.ts` CLI scaffolding |

### Phase 6: CI/CD & Quality (P2)

| # | Task |
|---|------|
| 6.1 | Create `.github/workflows/pathfinder.yml` |
| 6.2 | Create `.github/PULL_REQUEST_TEMPLATE.md` |
| 6.3 | Standardize all code to ESM |
| 6.4 | Fix all broken file references in docs |

---

## 9. Sources & References

### Superpowers (obra/superpowers)
- [GitHub Repository](https://github.com/obra/superpowers) — 3,787+ stars, MIT License
- [TDD Skill](https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md) — Iron Law, RED-GREEN-REFACTOR, anti-rationalization
- [Writing Skills Guide](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md) — TDD for documentation
- [DeepWiki Overview](https://deepwiki.com/obra/superpowers) — Architecture, skill composition, hooks
- [Claude Code Integration](https://deepwiki.com/obra/superpowers/5.1-claude-code:-skill-tool-and-hooks) — SessionStart hooks, slash commands
- [Superpowers to Turn Claude Code into a Senior Developer](https://betazeta.dev/blog/claude-code-superpowers/) — Practical guide
- [Stop AI Agents from Writing Spaghetti: Enforcing TDD with Superpowers](https://yuv.ai/blog/stop-ai-agents-from-writing-spaghetti-enforcing-tdd-with-superpowers) — Enforcement patterns
- [How I Force Claude Code to Plan Before Coding](https://www.trevorlasn.com/blog/superpowers-claude-code-skills) — Brainstorm → Plan → Execute workflow
- [Superpowers Skills Library on Claude Skills Market](https://skills.pawgrammer.com/skills/superpowers-skills-library) — Marketplace listing
- [Command Naming Issues (#244)](https://github.com/obra/superpowers/issues/244) — Slash command naming conventions

### Playwright CLI & Testing
- [Playwright CLI Official Docs](https://playwright.dev/docs/test-cli) — All commands, flags, and options
- [Deep Dive into Playwright CLI: Token-Efficient Browser Automation](https://testdino.com/blog/playwright-cli/) — `@playwright/cli` for AI agents
- [How to Use Playwright Codegen for Test Automation](https://www.browserstack.com/guide/how-to-use-playwright-codegen) — Test generation guide
- [Playwright Test Generator Docs](https://playwright.dev/docs/codegen) — Codegen reference
- [Running and Debugging Tests](https://playwright.dev/docs/running-tests) — Debug mode, trace viewer
- [Common Playwright Commands](https://ceroshjacob.medium.com/common-playwright-commands-f640e4e1b989) — Quick reference
- [Playwright CLI (BrowserStack)](https://www.browserstack.com/guide/playwright-cli) — Comprehensive overview
- [microsoft/playwright-cli GitHub](https://github.com/microsoft/playwright-cli) — CLI repository

### TDD with AI Agents
- [Test-Driven Development with AI — Builder.io](https://www.builder.io/blog/test-driven-development-ai)
- [Agentic TDD — Nizar's Blog](https://nizar.se/agentic-tdd/)
- [AI Agents, Meet Test Driven Development — Latent Space](https://www.latent.space/p/anita-tdd)
- [My LLM Coding Workflow Going Into 2026 — Addy Osmani](https://addyosmani.com/blog/ai-coding-workflow/)
- [Spec-Driven Development in 2025 — SoftwareSeni](https://www.softwareseni.com/spec-driven-development-in-2025-the-complete-guide-to-using-ai-to-write-production-code/)
- [How AI Code Assistants Are Revolutionizing TDD — Qodo](https://www.qodo.ai/blog/ai-code-assistants-test-driven-development/)
- [AI Coding Best Practices in 2025 — DEV Community](https://dev.to/ranndy360/ai-coding-best-practices-in-2025-4eel)

### REST API & Design Patterns
- [Best Practices for REST API Design — Stack Overflow](https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/)
- [API Design Patterns for REST — Stoplight](https://blog.stoplight.io/api-design-patterns-for-rest-web-services)
- [CRUD API Design Recommendations — Stoplight](https://blog.stoplight.io/crud-api-design)
- [Best Practices in API Design — Swagger](https://swagger.io/resources/articles/best-practices-in-api-design/)

### AI Agent Skills Ecosystem
- [How to Sync AI Skills Across Claude Code, OpenClaw, and Codex](https://dev.to/runkids/how-to-sync-ai-skills-across-claude-code-openclaw-and-codex-in-2-minutes-226e)
- [Awesome Agent Skills Repository](https://github.com/VoltAgent/awesome-agent-skills)
- [Pick Your Agent: Use Claude and Codex on Agent HQ — GitHub Blog](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/)

---

*This proposal was generated through comprehensive codebase analysis, deep research into [obra/superpowers](https://github.com/obra/superpowers) patterns, and [Playwright CLI](https://playwright.dev/docs/test-cli) best practices as of February 2026.*
