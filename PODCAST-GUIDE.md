# Pathfinder: The Complete Guide

**A podcast-ready deep dive into Pathfinder — the TDD methodology-as-code system for AI coding agents**

*Version 0.4.0 | Built on Playwright + Superpowers patterns*

---

## Table of Contents

1. [What Is Pathfinder?](#1-what-is-pathfinder)
2. [The Problem It Solves](#2-the-problem-it-solves)
3. [The Expedition Metaphor](#3-the-expedition-metaphor)
4. [Architecture: The Five Layers](#4-architecture-the-five-layers)
5. [How It Boots Up: The SessionStart Hook](#5-how-it-boots-up-the-sessionstart-hook)
6. [The 12 Composable Skills](#6-the-12-composable-skills)
7. [The 5-Phase Workflow in Detail](#7-the-5-phase-workflow-in-detail)
8. [Slash Commands: The Quick Entry Points](#8-slash-commands-the-quick-entry-points)
9. [The Anti-Rationalization Engine](#9-the-anti-rationalization-engine)
10. [Playwright Integration Under the Hood](#10-playwright-integration-under-the-hood)
11. [Unit Testing with Vitest](#11-unit-testing-with-vitest)
12. [Git Workflow: Branches, Commits, and Pull Requests](#12-git-workflow-branches-commits-and-pull-requests)
13. [The Checkpoint Fixture: Custom Test Instrumentation](#13-the-checkpoint-fixture-custom-test-instrumentation)
14. [The Custom Reporter: From Tests to Structured Data](#14-the-custom-reporter-from-tests-to-structured-data)
15. [The JSON Data Pipeline](#15-the-json-data-pipeline)
16. [Multi-Agent Dispatch and Two-Stage Review](#16-multi-agent-dispatch-and-two-stage-review)
17. [CI/CD Integration](#17-cicd-integration)
18. [Step-by-Step Usage Guide](#18-step-by-step-usage-guide)
19. [How to Extend Pathfinder: Writing New Skills](#19-how-to-extend-pathfinder-writing-new-skills)
20. [Inspirations and Credits](#20-inspirations-and-credits)

---

## 1. What Is Pathfinder?

Pathfinder is a **Test-Driven Development methodology encoded as executable code** for AI coding agents. It's not a library you `import`. It's not a framework you install. It's a *system of behavioral constraints* that transforms how an AI agent approaches software development.

Think of it this way: when you hire a human developer, they come with years of training, habits, and professional discipline. They know to write tests before code. They know to gather requirements before building. They know to verify their work before claiming it's done. An AI agent, by default, has none of these habits. It will happily write code without tests, skip requirements gathering, and claim completion without evidence.

Pathfinder gives AI agents that discipline.

It does this through 12 composable skill files that get loaded into the agent's context at the right time, a hook system that auto-injects behavioral rules at session start, and a complete Playwright-based testing pipeline that produces structured, machine-readable evidence of what was tested and what passed.

The name comes from the expedition metaphor that runs through the entire system: you're not just writing software, you're **charting unknown territory**. Every feature is a journey. Every test is a trail marker. Every passing test clears that marker. And when the expedition is complete, you have a map that proves every inch of the territory was explored.

---

## 2. The Problem It Solves

AI coding agents have a specific, well-documented set of failure modes:

**They skip requirements gathering.** Given "build a login page," an agent will immediately start writing JSX. It won't ask about error states, OAuth providers, session persistence, or accessibility. The result is code that handles the happy path and nothing else.

**They write tests after code — or not at all.** When an agent writes tests after implementation, those tests are biased. They test what the code *does*, not what it *should do*. They pass immediately, which means they never actually verified anything. A test that never failed is a test that never tested.

**They claim completion without evidence.** An agent will say "all tests pass" without running them. It will say "I verified the error handling" without actually triggering an error. It will say "the feature works" based on reading the code, not executing it.

**They rationalize shortcuts.** This is the most insidious failure. An agent doesn't just skip steps — it *explains why skipping was the right call*. "This is too simple to test." "I already know the requirements." "I'll add tests later." These sound reasonable. They're not.

**They have no enforcement mechanism.** Traditional AGENTS.md files are advisory. They say "please do TDD" and the agent says "sure" and then doesn't. There's no gate, no verification, no consequence for skipping.

Pathfinder solves all five problems through a combination of architectural enforcement (hooks that inject rules automatically), anti-rationalization tables (that preempt every known excuse), and a structured data pipeline (that requires machine-verifiable evidence before any claim of completion).

---

## 3. The Expedition Metaphor

Every concept in Pathfinder maps to an exploration metaphor:

| Software Concept | Pathfinder Term | Meaning |
|-----------------|----------------|---------|
| Feature/user story | **Journey** | A complete path through the application |
| Test case | **Checkpoint** | A specific point that must be verified |
| Test status | **Trail Marker** | Visual indicator of checkpoint state |
| Writing tests | **Scouting** | Exploring the trail ahead, marking dangers |
| Implementing code | **Building** | Constructing the trail others will follow |
| Requirements gathering | **Surveying** | Understanding the terrain before entering |
| Visual flow diagram | **Trail Map** | Mermaid diagram of the journey |
| Test runner | **Dispatch** | Coordinating scout and builder agents |
| PR/completion | **Expedition Report** | Evidence-based documentation of the journey |

### Trail Markers

The trail marker system is the visual heartbeat of Pathfinder:

| Marker | Name | Meaning |
|--------|------|---------|
| ❌ | **Uncharted** | Checkpoint identified, no test exists yet |
| 🔄 | **Scouted** | Test written, awaiting implementation (RED phase) |
| ✅ | **Cleared** | Test passing (GREEN phase) |
| ⚠️ | **Unstable** | Flaky test that needs investigation |
| ⏭️ | **Skipped** | Intentionally out of scope for this expedition |

These markers appear everywhere: in Mermaid diagrams, in checkpoint tables, in the custom reporter output, and in PR templates. At any point, anyone (human or machine) can glance at the markers and know exactly how far the expedition has progressed.

---

## 4. Architecture: The Five Layers

Pathfinder is organized into five layers, from the most abstract (enforcement) to the most concrete (platform):

```
┌─────────────────────────────────────┐
│  Layer 1: ENFORCEMENT               │  ← SessionStart hook, The Rule,
│  (What agents MUST do)              │     anti-rationalization tables
├─────────────────────────────────────┤
│  Layer 2: METHODOLOGY               │  ← 7-phase workflow, composable
│  (How agents work)                  │     skills, slash commands
├─────────────────────────────────────┤
│  Layer 3: INTEGRATION               │  ← Checkpoint fixture, custom
│  (How code connects to tests)       │     reporter, data pipeline
├─────────────────────────────────────┤
│  Layer 4: TOOLING                   │  ← Playwright CLI commands,
│  (What agents run)                  │     npm scripts, coverage tools
├─────────────────────────────────────┤
│  Layer 5: PLATFORM                  │  ← Playwright Test, TypeScript,
│  (What runs underneath)            │     Node.js, GitHub Actions
└─────────────────────────────────────┘
```

### Layer 1: Enforcement

This is what makes Pathfinder different from a documentation file. The enforcement layer uses three mechanisms:

1. **SessionStart Hook** — Automatically injects the meta-skill into every agent session
2. **The Rule** — "If there is even a 1% chance a skill applies, you MUST invoke it"
3. **Anti-Rationalization Tables** — Preemptive counters to every known excuse for skipping

### Layer 2: Methodology

The 12 composable skills and 4 slash commands that define HOW work gets done. Each skill is a self-contained Markdown file with goals, prerequisites, step-by-step processes, CLI commands, and anti-rationalization tables.

### Layer 3: Integration

The custom Playwright fixture (`checkpoint`) and custom reporter (`PathfinderReporter`) that bridge the gap between test execution and structured data. This is the layer that turns "tests passed" into machine-readable evidence.

### Layer 4: Tooling

The npm scripts and Playwright CLI commands that agents actually execute. `npx playwright test --grep "AUTH-01"`, `npx playwright codegen`, `npx playwright show-trace`, etc.

### Layer 5: Platform

Playwright Test as the native test runner, TypeScript for type safety, Node.js as the runtime, and GitHub Actions for CI/CD.

---

## 5. How It Boots Up: The SessionStart Hook

This is where everything begins. When an AI coding agent starts a session in a Pathfinder project, the hook system fires before the agent does anything else.

### The Hook File

```
hooks/hooks.json
```

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

### What Happens

1. Agent session begins (startup, resume, clear, or compact event)
2. Hook system matches the event against `"startup|resume|clear|compact"`
3. Hook executes `cat skills/using-pathfinder/SKILL.md`
4. The meta-skill content is injected directly into the agent's context
5. The agent now has The Rule, the skill routing table, enforcement gates, and anti-skip guards loaded *before it reads any user instructions*

### Why This Matters

This is inspired directly by the **obra/superpowers** project's `using-superpowers` pattern. The key insight: if you wait for the agent to *decide* to follow TDD practices, it won't. The rules must be injected *before* the agent even knows what task it's working on. By the time the user says "build me a login page," the agent already has the Pathfinder methodology loaded and knows it must start with surveying, not coding.

The hook fires on four events:
- **startup** — Fresh session
- **resume** — Continuing a previous session
- **clear** — Context was cleared
- **compact** — Context was compressed

This ensures the rules are always present, even if the agent's context was wiped.

---

## 6. The 12 Composable Skills

Skills are the building blocks of Pathfinder. Each one is a standalone Markdown file in the `skills/` directory with YAML frontmatter, a clear goal, step-by-step instructions, CLI commands, and anti-rationalization tables.

### Why 12?

The system has 12 composable skills, consolidated from the original design. Overlapping skills were merged (charting + marking → planning, TDD enforcement absorbed into scouting/building, verification absorbed into reporting, writing-skills moved to docs/), and two new skills were added to fill real gaps (code-review and security). The result: fewer skills, sharper focus, less duplication, better coverage.

### The Skill Roster

#### Meta-Skill

**1. `using-pathfinder`** — Auto-injected at session start via SessionStart hook. Contains The Rule, the 12-skill routing table, enforcement gates, trail markers, and the anti-skip guard. This is the "brain" that routes to every other skill.

#### Phase Skills (follow the 5-phase workflow)

**2. `surveying` (Phase 1)** — Requirements gathering through Socratic dialogue. Reads project context, asks questions one at a time (multiple choice preferred), identifies hazards (errors, empty states, edge cases, auth), proposes 2-3 approaches with trade-offs. YAGNI check: "Can any requirements be removed?"

**3. `planning` (Phase 2)** — Charts a Mermaid journey map AND extracts all checkpoints in one pass. Combines the old charting and marking skills. Defines node format, checkpoint naming (`AUTH-01`), categories (Happy Path, Error, Empty State, Edge Case), edge case matrix. Presents incrementally with approval checks. Commits before scouting.

**4. `scouting` (Phase 3)** — Writes failing tests for ALL checkpoints using both Playwright (E2E) and Vitest (unit). The Iron Law: "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST." Includes codegen-assisted scouting, RED verification for both layers, red flags list (6 signs TDD was abandoned), and testing anti-patterns table. Territory: `e2e/` + `src/**/*.test.ts`.

**5. `building` (Phase 4)** — Implements minimal code to pass each test, one at a time. Unit test FAIL → E2E test FAIL → write code → unit PASS → E2E PASS → commit. Includes debugging commands, verification checklist for both layers, and explicit Scout/Builder mode switching protocol.

**6. `reporting` (Phase 6)** — Verifies all evidence, creates PR, closes the expedition. Absorbs the old verification-before-completion skill: required-evidence-per-claim table, pre-review checklist, PR creation commands (`gh pr create`), post-PR review workflow, issue severity levels.

#### Optional Phase Skill

**7. `dispatching` (Phase 5, optional)** — Multi-agent coordination with fresh context dispatch. Only needed when Scout and Builder are separate agents. Provides dispatch templates, two-stage review (trail compliance + code quality), handoff protocol, and single-agent mode guidance.

#### Cross-Cutting Skills (apply at any phase)

**8. `unit-testing`** — Vitest enforcement for functions, modules, and components. Defines when unit tests are required vs when E2E is preferred. Co-located test files, checkpoint naming with `U` suffix (`AUTH-U01`), watch mode for rapid RED-GREEN cycles.

**9. `git-workflow`** — Branch naming (`expedition/`, `scout/`, `fix/`), commit conventions (`Scout: Mark trail for AUTH-01`), step-by-step PR creation, multi-agent branch strategy.

**10. `code-review`** — Structured review process: understand the expedition, run tests yourself, trail compliance review, code quality review, security spot-check. Feedback format with severity levels. Anti-patterns: rubber-stamping, only reviewing latest commit, nitpicking style over logic.

**11. `security`** — Security checklist for every phase: input validation, auth/authz, data protection, output encoding, dependency auditing. Example security checkpoint tests (XSS, SQL injection, auth bypass). CLI commands for auditing. Integrated into the planning and reporting phases.

**12. `systematic-debugging`** — Root-cause investigation: Reproduce → Isolate → Diagnose → Fix → Verify. Playwright debugging commands. Fix step requires a test that reproduces the bug FIRST. Flaky test protocol: mark ⚠️, run 10x, fix, run 10x again.

---

## 7. The 5-Phase Workflow in Detail

This is the complete lifecycle of a feature in Pathfinder. Streamlined from the original 7 phases by merging Chart+Mark into Plan, and absorbing Dispatch into the workflow as optional.

### Phase 1: Survey (`/survey`)

**When:** A new feature, user story, or requirement appears.
**What happens:**
1. Agent reads project files, docs, recent commits
2. Asks clarifying questions one at a time (multiple choice preferred)
3. Identifies all hazards (errors, empty states, edge cases, auth issues)
4. Proposes 2-3 approaches with trade-offs
5. Gets user sign-off before proceeding

**Output:** Approved requirements and chosen approach.

### Phase 2: Plan

**When:** Survey is approved.
**What happens:**
1. Agent creates a Mermaid diagram in `USER-JOURNEYS.md` with all checkpoint nodes
2. Extracts checkpoints into a structured list (ID, category, description, priority)
3. Creates edge case matrix
4. Presents incrementally — happy path first, then errors, then edge cases
5. YAGNI check: can any checkpoints be removed?
6. Commits map and checkpoints BEFORE any tests are written

**Output:** Committed trail map and checkpoint list with all markers ❌ (Uncharted).

### Phase 3: Scout (`/scout`)

**When:** Plan is approved with checkpoints.
**What happens:**
1. Agent writes failing E2E tests (Playwright) AND unit tests (Vitest) for ALL checkpoints
2. E2E tests use the custom checkpoint fixture (`checkpoint.mark()`, `checkpoint.clear()`)
3. Unit tests use co-located files (`src/**/*.test.ts`) with `U` suffix IDs (`AUTH-U01`)
4. For complex flows, uses `npx playwright codegen` to record interactions
5. Adds tests codegen can't capture: error states, empty states, edge cases
6. Verifies RED for both layers — every test must be seen to fail
7. Updates markers: ❌ → 🔄
8. Commits: "Scout: Mark trail for FEAT-01 through FEAT-05 (E2E + unit)"

**Territory:** `e2e/` for E2E tests, `src/**/*.test.ts` for unit tests. Cannot touch implementation code.

**Output:** All tests exist and fail. Trail map shows all 🔄.

### Phase 4: Build (`/build`)

**When:** All tests exist and fail.
**What happens (for EACH checkpoint, one at a time):**
1. Run unit test → watch it FAIL
2. Run E2E test → watch it FAIL
3. Write the simplest code to make both pass
4. Run full suite to check for regressions (`npm run test:all`)
5. Update marker: 🔄 → ✅
6. Commit: "Builder: Clear FEAT-01"

If tests need fixing, the builder explicitly announces "Entering Scout mode" before touching test code.

**Territory:** `src/` implementation code ONLY. Cannot modify test assertions.

**Output:** All checkpoints pass. Trail map shows all ✅.

### Phase 5: Report (`/report`)

**When:** All checkpoints are ✅.
**What happens:**
1. Run full suite: `npm run test:all`
2. Generate HTML report: `npx playwright test --reporter=html`
3. Update coverage: `npm run test:coverage`
4. Generate trail map: `npm run test:generate-map`
5. Create PR with evidence using `gh pr create` and the expedition report template

**Output:** Pull request with complete evidence trail.

---

## 8. Slash Commands: The Quick Entry Points

Pathfinder provides four slash commands as shortcuts into the workflow:

### `/survey`
Invokes the `pathfinder:surveying` skill. Begins terrain survey with Socratic questioning. Use when starting a new feature or story.

### `/scout`
Invokes the `pathfinder:scouting` skill. Requires a charted trail map in `USER-JOURNEYS.md`. Writes failing tests for all checkpoints. Includes Playwright codegen commands for recording interactions.

### `/build`
Invokes the `pathfinder:building` skill. Requires all checkpoint tests to exist and fail (🔄 status). Implements minimal code one checkpoint at a time using the RED-GREEN loop.

### `/report`
Invokes the `pathfinder:reporting` skill. Requires all checkpoints to be ✅. Generates the expedition report with full evidence, creates the PR.

Each slash command file has `disable-model-invocation: true` in its frontmatter, meaning it injects instructions into the agent's context without making a separate API call. This is more efficient and keeps the agent in its current conversation flow.

---

## 9. The Anti-Rationalization Engine

This is arguably Pathfinder's most innovative feature, and it comes directly from the obra/superpowers project.

### The Problem

AI agents don't just skip steps — they *justify* skipping steps. And their justifications sound reasonable:

- "This is too simple to test" → Sounds sensible, but simple code breaks most often
- "I'll write tests after" → Sounds pragmatic, but tests-after are implementation-biased
- "I already know the requirements" → Sounds efficient, but assumptions cause 3x rework
- "I'll save time by skipping" → Sounds productive, but you won't save time

### The Solution

Every skill in Pathfinder contains an **anti-rationalization table** — a two-column table that maps each known rationalization to a counter-argument. These aren't vague. They're specific, pre-written responses to exact phrases the agent would use.

Here's the one from the TDD skill (the most comprehensive):

| Rationalization | Why It's Wrong | What To Do |
|----------------|---------------|-----------|
| "This is too simple to test" | Simple code breaks most often. A 1-line regex can have 10 edge cases. | Write the test. It'll take 30 seconds. |
| "I'll write tests after" | Tests-after verify YOUR implementation. Tests-first verify THE REQUIREMENT. | Delete the code. Write the test first. |
| "I already manually verified" | Manual testing is ad-hoc and unreproducible. | Not evidence. Write the test. |
| "Deleting working code is wasteful" | Sunk cost fallacy. Unverified code is technical debt. | Delete it. Test-first will be better. |
| "The test passed immediately" | It doesn't test new behavior. It's wrong. | Rewrite to test the NEW requirement. |
| "I just need to fix this quickly" | Scope creep starts here. One quick fix becomes three. | Stop. Survey first. |
| "The tests are in my head" | Invisible tests can't catch regressions or be automated. | Write them in code. Now. |
| "I'll keep code as reference" | You'll write tests that validate implementation, not requirements. | Close the file. Delete. Fresh start. |

### How It Works Under the Hood

When the meta-skill is loaded via SessionStart, it includes the anti-skip guard:

| Thought | Reality | Action |
|---------|---------|--------|
| "This is too trivial for the full workflow" | Trivial things break most often | At minimum invoke `pathfinder:scouting` |
| "I already know the requirements" | Assumptions cause rework | Invoke `pathfinder:surveying` |
| "Tests will slow me down" | Tests catch the bugs you'd spend 10x fixing later | Invoke `pathfinder:test-driven-development` |
| "I'll add tests after" | Tests-after are biased by implementation | Delete code, invoke `pathfinder:scouting` |

Then, when the agent loads any individual skill, that skill has its OWN anti-rationalization table specific to its phase. The surveying skill counters "The requirements are obvious." The scouting skill counters "I'll write tests and code together." The building skill counters "I'll implement multiple checkpoints at once."

The result is a **layered defense**: the meta-skill catches general excuses, and each phase skill catches phase-specific excuses. There's no known rationalization that doesn't have a pre-written counter.

---

## 10. Playwright Integration Under the Hood

Pathfinder chose Playwright as its testing platform and deeply integrates with Playwright CLI. Here's how every major Playwright feature maps to the expedition workflow:

### Configuration (`playwright.config.ts`)

```typescript
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,      // Can't leave .only in CI
  retries: process.env.CI ? 2 : 0,    // Retry in CI, not locally
  workers: process.env.CI ? 1 : undefined, // Sequential in CI
  reporter: [
    ['list'],                           // Console output
    ['html', { open: 'never' }],        // HTML evidence report
    ['json', { outputFile: 'test-results/results.json' }],  // Raw JSON
    ['./e2e/reporters/pathfinder-reporter.ts'],  // Custom checkpoint reporter
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    screenshot: 'on',                   // Always capture screenshots
    trace: 'on-first-retry',           // Capture trace on retry
    video: 'on-first-retry',           // Capture video on retry
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },  // Auth runs first
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: '.auth/state.json' },
      dependencies: ['setup'],  // Tests depend on auth
    },
  ],
});
```

Key design decisions:
- **Four reporters run simultaneously** — list for console, html for evidence, json for raw data, custom for checkpoints
- **Screenshots always on** — Evidence is not optional
- **Traces on first retry** — When a test flakes, you get a full timeline
- **Auth as a project dependency** — Login happens once, state is reused across all tests
- **`forbidOnly` in CI** — Prevents accidentally leaving `.only()` in committed tests

### Auth Setup (`e2e/auth.setup.ts`)

The auth setup uses Playwright's native project dependency system instead of a custom script:

- No `waitForTimeout` anti-patterns — uses Playwright auto-waiting
- Handles OAuth consent screens gracefully with `isVisible` catch
- Saves auth state to `.auth/state.json` for reuse by all tests
- Environment variables (`TEST_EMAIL`, `TEST_PASSWORD`) from `.env.local`

### CLI Command Map

Every Playwright CLI command has a specific role in the expedition:

| Command | Phase | Purpose |
|---------|-------|---------|
| `npx playwright codegen` | Scout | Record user interactions to generate test code |
| `npx playwright codegen --load-storage=.auth/state.json` | Scout | Record while authenticated |
| `npx playwright test --grep "FEAT-01"` | Scout/Build | Run a single checkpoint test |
| `npx playwright test --reporter=list` | Build/Report | Run all tests with detailed output |
| `npx playwright test --debug` | Build | Step-through debugging in headed browser |
| `npx playwright test --headed` | Build | Watch the browser execute tests |
| `npx playwright test --trace=on` | Debug | Capture full execution trace |
| `npx playwright show-trace <path>` | Debug | Open trace viewer with timeline, screenshots, network |
| `npx playwright test --reporter=html` | Report | Generate HTML evidence report |
| `npx playwright show-report` | Report | Open HTML report in browser |
| `npx playwright test --last-failed` | Debug | Re-run only tests that failed last time |
| `npx playwright test --repeat-each=10` | Debug | Run test 10x to check for flakiness |
| `npx playwright test --retries=2` | CI | Retry failed tests (catches intermittent failures) |
| `npx playwright test --shard=1/3` | CI | Distribute tests across parallel workers |

### npm Script Shortcuts

All commands are also available as npm scripts for convenience:

```json
{
  "test":            "playwright test",
  "test:unit":       "vitest run",
  "test:unit:watch": "vitest",
  "test:all":        "vitest run && playwright test",
  "test:setup":      "playwright test --project=setup",
  "test:headed":     "playwright test --headed",
  "test:debug":      "playwright test --debug",
  "test:report":     "playwright show-report",
  "test:codegen":    "playwright codegen --load-storage=.auth/state.json",
  "test:coverage":   "tsx scripts/update-coverage.ts",
  "test:trace":      "playwright show-trace",
  "test:generate-map": "tsx scripts/generate-map.ts"
}
```

---

## 11. Unit Testing with Vitest

While Playwright handles E2E testing (verifying what the **user sees**), Vitest handles unit testing (verifying what the **code does**). Both layers are required in Pathfinder. Here's how unit testing fits into the system.

### Why Two Testing Layers?

| Layer | Tool | Tests | Speed | Tells You |
|-------|------|-------|-------|-----------|
| **Unit** | Vitest | Individual functions, modules, components | Fast (milliseconds) | **What** broke |
| **E2E** | Playwright | Full user journeys in a real browser | Slow (seconds) | **That something** broke |

An E2E test that fails tells you "the login page is broken." A unit test that fails tells you "the `validateEmail` function rejects valid emails when they contain a `+` character." You need both signals.

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
    exclude: ['e2e/**', 'node_modules/**'],
    reporters: ['verbose', 'json'],
    outputFile: 'test-results/unit-results.json',
  },
});
```

Key decisions:
- **Tests live in `src/`** — Co-located next to the code they test, not in a separate directory
- **E2E tests excluded** — Vitest only runs unit tests; Playwright handles E2E
- **JSON output** — Results written to `test-results/` for pipeline consumption

### Checkpoint Naming Convention

Unit checkpoints use a `U` suffix to distinguish them from E2E checkpoints:

| Type | Format | Example |
|------|--------|---------|
| E2E | `AUTH-01` | `AUTH-01: Login redirects to dashboard` |
| Unit | `AUTH-U01` | `AUTH-U01: validateEmail rejects empty string` |

Both types appear in the same trail map, giving complete visibility.

### Co-Located Test Files

```
src/
├── utils/
│   ├── validate-email.ts          ← Implementation
│   └── validate-email.test.ts     ← Unit test (right next to it)
├── hooks/
│   ├── use-auth.ts
│   └── use-auth.test.ts
├── api/
│   ├── login.ts
│   └── login.test.ts
```

If you see a `.ts` file without a `.test.ts` beside it, that's a red flag — the code is untested.

### Unit Test Example

```typescript
// src/utils/validate-email.test.ts
import { describe, it, expect } from 'vitest';
import { validateEmail } from './validate-email';

describe('Auth Journey — Unit', () => {
  it('AUTH-U01: validateEmail rejects empty string', () => {
    expect(validateEmail('')).toBe(false);
  });

  it('AUTH-U02: validateEmail rejects missing @', () => {
    expect(validateEmail('userexample.com')).toBe(false);
  });

  it('AUTH-U03: validateEmail accepts valid email', () => {
    expect(validateEmail('user@example.com')).toBe(true);
  });
});
```

### CLI Commands

```bash
# Run all unit tests
npm run test:unit

# Run specific test file
npx vitest run src/utils/validate-email.test.ts

# Run by checkpoint name
npx vitest run --testNamePattern "AUTH-U01"

# Watch mode (re-runs on file change)
npm run test:unit:watch

# Run BOTH unit and E2E
npm run test:all
```

### Who Is Responsible?

| Role | Unit Tests | E2E Tests |
|------|-----------|-----------|
| **Scout** | Writes failing unit tests (`src/**/*.test.ts`) | Writes failing E2E tests (`e2e/`) |
| **Builder** | Makes unit tests pass | Makes E2E tests pass |

The Scout writes BOTH types of tests before the Builder writes any implementation code. The Builder must pass BOTH layers before claiming a checkpoint is cleared.

### The Extended Build Loop

```bash
# 1. Unit test — FAIL
npx vitest run --testNamePattern "AUTH-U01"

# 2. E2E test — FAIL
npx playwright test --grep "AUTH-01"

# 3. Write minimal code

# 4. Unit test — PASS
npx vitest run --testNamePattern "AUTH-U01"

# 5. E2E test — PASS
npx playwright test --grep "AUTH-01"

# 6. Full suite — no regressions
npm run test:all
```

---

## 12. Git Workflow: Branches, Commits, and Pull Requests

The original Pathfinder had no guidance on branching, commits, or PR creation. The reporting skill said "create a PR" without explaining how. The `git-workflow` skill fills this gap with a complete git strategy designed around the expedition lifecycle.

### Branch Strategy

Every expedition gets its own branch. Never work directly on `main`.

**Branch naming convention:** `<role>/<journey>-<short-description>`

| Prefix | When | Example |
|--------|------|---------|
| `expedition/` | Single agent, full expedition | `expedition/auth-login-flow` |
| `scout/` | Scout-only branch (multi-agent) | `scout/auth-login-flow` |
| `builder/` | Builder-only branch (multi-agent) | `builder/auth-login-flow` |
| `fix/` | Bug fixes | `fix/auth-token-expiry` |
| `hotfix/` | Critical production fixes | `hotfix/auth-session-crash` |

**When to create:** After Survey is approved, before Scouting begins. The Scout's first commit (tests + trail map) should already be on the expedition branch.

```bash
git checkout main
git pull origin main
git checkout -b expedition/auth-login-flow
git push -u origin expedition/auth-login-flow
```

### Commit Conventions

Every commit message follows the pattern: `<Role>: <Action> <checkpoint-range>`

| Phase | Example |
|-------|---------|
| Survey | `Survey: Chart requirements for auth login` |
| Chart | `Chart: Map auth journey with 5 checkpoints` |
| Mark | `Mark: Define checkpoints AUTH-01 through AUTH-05` |
| Scout | `Scout: Mark trail for AUTH-01 through AUTH-05` |
| Build | `Builder: Clear AUTH-01` |
| Report | `Report: Expedition complete for auth journey` |

Key rules:
- **One checkpoint per commit during Build** — enables `git bisect`
- **Scout and Builder work never in the same commit** — clean role separation in git history
- **Checkpoint IDs in every message** — `git log --oneline` becomes a trail map

### PR Creation

After all checkpoints are ✅:

```bash
# Final commit
git add USER-JOURNEYS.md checkpoints.json
git commit -m "Report: Expedition complete for auth journey"

# Push and create PR
git push origin expedition/auth-login-flow
gh pr create \
  --base main \
  --head expedition/auth-login-flow \
  --title "Expedition: Auth Login Flow (AUTH-01 through AUTH-05)" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md
```

The PR body uses the expedition report template with trail map, checkpoint table, coverage stats, and evidence links.

### Multi-Agent Branch Strategy

**Single branch (recommended):** Scout creates branch, commits tests. Builder pulls same branch, implements, commits per checkpoint. One PR at the end.

**Separate branches (complex):** Scout works on `scout/auth-login-flow`, Builder branches from it to `builder/auth-login-flow`. Two PRs — Scout into expedition, Builder into main.

---

## 13. The Checkpoint Fixture: Custom Test Instrumentation

The checkpoint fixture is the bridge between Playwright tests and the Pathfinder trail marker system. It's a custom Playwright fixture defined in `e2e/fixtures/pathfinder.ts`.

### How It Works

```typescript
import { test as base, expect } from '@playwright/test';

export const test = base.extend<PathfinderFixtures>({
  checkpoint: async ({}, use, testInfo) => {
    const markers: TrailMarker[] = [];

    await use({
      mark(id, description) {
        // Adds a marker with 'scouted' status and records it as a test annotation
        markers.push({ id, description, status: 'scouted', timestamp: new Date().toISOString() });
        testInfo.annotations.push({ type: 'checkpoint', description: `${id}: ${description}` });
      },

      clear(id) {
        // Updates the marker to 'cleared' status — the test assertion passed
        const marker = markers.find(m => m.id === id);
        if (marker) { marker.status = 'cleared'; marker.timestamp = new Date().toISOString(); }
      },

      skip(id, reason) {
        // Marks as 'skipped' with a reason, also adds to test annotations
        const marker = markers.find(m => m.id === id);
        if (marker) { marker.status = 'skipped'; marker.timestamp = new Date().toISOString(); }
        testInfo.annotations.push({ type: 'skip', description: `${id}: ${reason}` });
      },

      getMarkers() {
        return [...markers];
      },
    });

    // AFTER THE TEST: Write markers as JSON for the reporter to consume
    if (markers.length > 0) {
      const resultFile = `test-results/markers-${testInfo.testId.replace(/[^a-zA-Z0-9]/g, '-')}.json`;
      fs.writeFileSync(resultFile, JSON.stringify(markers, null, 2));
    }
  },
});
```

### Usage in Tests

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

### The Lifecycle

1. **`checkpoint.mark('AUTH-01', 'description')`** — Called at the start of the test. Creates a trail marker with `scouted` status. Also adds a Playwright annotation so the marker shows up in Playwright's own reporting.

2. **Test assertions run** — Standard Playwright `expect()` calls verify the behavior. If any assertion fails, the test fails and `clear()` is never called.

3. **`checkpoint.clear('AUTH-01')`** — Called at the end of the test, AFTER all assertions pass. Updates the marker to `cleared` status.

4. **After test teardown** — The fixture writes all markers to a JSON file in `test-results/`. Each test gets its own marker file, keyed by test ID.

### Why This Design?

The marker starts as `scouted` (test exists) and only becomes `cleared` (test passes) if ALL assertions in between succeed. If the test fails, the marker stays `scouted`. This creates a structural guarantee: you can't have a `cleared` marker without a passing test.

The JSON files written to `test-results/` are consumed by the PathfinderReporter, completing the data pipeline.

---

## 14. The Custom Reporter: From Tests to Structured Data

The PathfinderReporter (`e2e/reporters/pathfinder-reporter.ts`) is a custom Playwright reporter that extracts checkpoint information from test results and produces structured JSON output.

### How It Works

```typescript
class PathfinderReporter implements Reporter {
  private checkpoints: Map<string, CheckpointResult> = new Map();

  onBegin() {
    // Prints the trail reporter header
    console.log('🗺️  Pathfinder Trail Reporter');
  }

  onTestEnd(test: TestCase, result: TestResult) {
    // Extracts checkpoint ID from test title using regex: "AUTH-01: Login redirects"
    const match = test.title.match(/^([A-Z]+-\d+):\s*(.+)/);
    if (!match) return;  // Skip non-checkpoint tests

    const [, id, description] = match;

    // Maps Playwright status to trail marker status
    const status = result.status === 'passed' ? 'pass'
                 : result.status === 'skipped' ? 'skip'
                 : 'fail';

    // Stores the checkpoint with journey, duration, and error info
    this.checkpoints.set(id, { id, description, status, durationMs: result.duration, ... });

    // Prints live trail marker to console
    console.log(`  ✅ AUTH-01: Login redirects to dashboard (245ms)`);
  }

  onEnd(result: FullResult) {
    // Calculates coverage summary
    const passed = checkpoints.filter(c => c.status === 'pass').length;
    const coverage = Math.round((passed / total) * 100);

    // Writes structured JSON to test-results/checkpoints.json
    const output = {
      timestamp: new Date().toISOString(),
      summary: { passed, failed, skipped, total, coverage },
      checkpoints: { 'AUTH-01': {...}, 'AUTH-02': {...}, ... }
    };
    fs.writeFileSync('test-results/checkpoints.json', JSON.stringify(output, null, 2));

    // Prints trail map summary to console
    console.log('✅ Cleared: 12');
    console.log('❌ Blocked: 1');
    console.log('📊 Coverage: 92% (12/13)');
  }
}
```

### The Key Design Decision

The reporter extracts checkpoint IDs from **test titles**, not from annotations or special comments. This means:

- Test titles MUST follow the format: `"CHECKPOINT-ID: Description"`
- Example: `"AUTH-01: Login redirects to dashboard"`
- The regex `^([A-Z]+-\d+):\s*(.+)` extracts the ID and description

This convention is enforced by the skill files. Every scouting and TDD skill example shows the correct format. Any test that doesn't match the pattern is simply ignored by the reporter (it's not a checkpoint test).

### Output Format

The reporter produces `test-results/checkpoints.json`:

```json
{
  "timestamp": "2026-02-10T15:30:00.000Z",
  "durationMs": 12450,
  "status": "passed",
  "summary": {
    "passed": 12,
    "failed": 1,
    "skipped": 0,
    "total": 13,
    "coverage": 92
  },
  "checkpoints": {
    "AUTH-01": {
      "id": "AUTH-01",
      "description": "Login redirects to dashboard",
      "status": "pass",
      "durationMs": 245,
      "journey": "Auth Journey"
    },
    "AUTH-02": {
      "id": "AUTH-02",
      "description": "Invalid credentials show error",
      "status": "fail",
      "durationMs": 1200,
      "error": "Expected element to be visible",
      "journey": "Auth Journey"
    }
  }
}
```

---

## 15. The JSON Data Pipeline

This is one of Pathfinder's most important architectural decisions. The original system used regex to parse and update Markdown files — fragile, error-prone, and unmaintainable. The new system uses a structured JSON pipeline:

```
┌──────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│ npx playwright   │───▶│ PathfinderReporter    │───▶│ test-results/       │
│ test             │    │ (onTestEnd)           │    │ checkpoints.json    │
│                  │    │                       │    │ (reporter output)   │
└──────────────────┘    └──────────────────────┘    └─────────┬───────────┘
                                                              │
                                                              ▼
                                                    ┌─────────────────────┐
                                                    │ npm run             │
                                                    │ test:coverage       │
                                                    │ (update-coverage.ts)│
                                                    └─────────┬───────────┘
                                                              │
                                                              ▼
                                                    ┌─────────────────────┐
                                                    │ checkpoints.json    │
                                                    │ (state file)        │
                                                    │ Accumulated state   │
                                                    └─────────┬───────────┘
                                                              │
                                                              ▼
                                                    ┌─────────────────────┐
                                                    │ npm run             │
                                                    │ test:generate-map   │
                                                    │ (generate-map.ts)   │
                                                    └─────────┬───────────┘
                                                              │
                                                              ▼
                                                    ┌─────────────────────┐
                                                    │ USER-JOURNEYS.md    │
                                                    │ (human-readable)    │
                                                    │ Trail map document  │
                                                    └─────────────────────┘
```

### Step 1: Test Execution → Reporter Output

`npx playwright test` runs all tests. The PathfinderReporter (running alongside the standard reporters) extracts checkpoint data and writes `test-results/checkpoints.json`.

### Step 2: Reporter Output → State File

`npm run test:coverage` (which runs `tsx scripts/update-coverage.ts`) reads the reporter output and updates the persistent state file `checkpoints.json` in the project root. This state file accumulates results over time — it doesn't get wiped between runs. If you add new checkpoints, they're appended. If existing checkpoints change status, they're updated.

The coverage script also supports manual updates:
```bash
npx tsx scripts/update-coverage.ts --status WELL-01:pass,WELL-02:fail
```

### Step 3: State File → Trail Map

`npm run test:generate-map` (which runs `tsx scripts/generate-map.ts`) reads the state file and generates `USER-JOURNEYS.md` — a human-readable Markdown file with:

1. **Coverage summary table** — Per-journey coverage percentages
2. **Per-journey checkpoint tables** — ID, description, status marker, last run date
3. **Trail markers legend** — What each emoji means

### Why This Architecture?

1. **No regex parsing of Markdown** — The old system used regex to find and replace emoji in Mermaid diagrams. One malformed diagram would break the entire pipeline.
2. **Machine-readable intermediate format** — `checkpoints.json` can be consumed by any tool: CI scripts, PR comment generators, dashboards, the generate-map script.
3. **Accumulated state** — Results persist across runs. You don't lose history.
4. **Human-readable final output** — `USER-JOURNEYS.md` is still Markdown that anyone can read, but it's *generated* from structured data, not *edited* by hand.
5. **Separation of concerns** — The reporter just writes data. The coverage script manages state. The map generator creates the document. Each piece is independently testable.

---

## 16. Multi-Agent Dispatch and Two-Stage Review

Pathfinder supports a multi-agent workflow where different agents handle different roles, coordinated by the dispatching skill.

### The Fresh Context Principle

When you dispatch a subagent (a Scout or Builder), that agent starts with a clean context. It doesn't know what happened in previous conversations. This is actually a *feature*, not a bug — it prevents context pollution, hallucinated assumptions, and accumulated confusion.

But it means every dispatch must be **completely self-contained**. The dispatching skill provides copy-paste templates that include:

- Role and territory (Scout: `e2e/` only; Builder: `src/` only)
- Exact task description
- Relevant trail map section
- Checkpoint details with acceptance criteria
- CLI commands to run
- Expected results
- What to do when done

### Scout → Builder Handoff

```
@builder — Trail marked for AUTH-01 through AUTH-05.
Tests in e2e/auth.spec.ts. Map in USER-JOURNEYS.md.
Run: npx playwright test e2e/auth.spec.ts
All tests should FAIL (expected).
```

### Builder → Scout Handoff

```
@scout — Trail cleared. All checkpoints passing.
Evidence: test-results/ and playwright-report/
Ready for expedition report.
```

### Two-Stage Review

After each Builder completes a checkpoint, a review process runs:

**Stage 1: Trail Compliance**
- Does the implementation match the checkpoint description exactly?
- No extra features beyond what the checkpoint requires? (YAGNI)
- Was the test written BEFORE implementation? (check `git log`)
- Does screenshot evidence match expected behavior?
- Is the marker correctly updated?

If Stage 1 fails → Builder fixes → Re-review Stage 1.

**Stage 2: Code Quality**
Only runs after Stage 1 passes:
- Minimal code — simplest solution that passes the test?
- No console errors or warnings?
- No hardcoded values that should be configurable?
- Error handling for the checkpoint's edge cases?
- Code matches project conventions?

If Stage 2 fails → Builder fixes → Re-review Stage 2 only.

**Reviews loop until both stages pass.** No exceptions, no shortcuts.

### Single-Agent Mode

When one agent handles both roles (the common case):
1. Complete all Scout work first (write ALL tests, verify they FAIL)
2. Commit the scout work
3. Switch to Builder (implement without changing tests)
4. If tests need fixing — explicitly switch back to Scout
5. Never blur the boundary

---

## 17. CI/CD Integration

Pathfinder includes a complete GitHub Actions workflow in `.github/workflows/pathfinder.yml`.

### The Pipeline

```yaml
1. Checkout code
2. Setup Node.js 20 with npm cache
3. npm ci (clean install)
4. npx playwright install --with-deps chromium
5. npx playwright test (with CI environment variables)
6. npx tsx scripts/update-coverage.ts (always runs, even on failure)
7. Upload playwright-report/ artifact (14-day retention)
8. Upload test-results/ artifact (7-day retention)
9. Comment coverage on PR (if PR event)
```

### CI-Specific Behavior

The `playwright.config.ts` enables CI-specific settings:

- **`forbidOnly: !!process.env.CI`** — Prevents `.only()` from being committed
- **`retries: process.env.CI ? 2 : 0`** — Retries failed tests twice in CI (catches flakes)
- **`workers: process.env.CI ? 1 : undefined`** — Sequential execution in CI for stability

### PR Coverage Comment

When tests complete on a PR, a GitHub Script action reads `test-results/checkpoints.json` and posts a comment:

```
## 🗺️ Pathfinder Coverage: 92% ✅

✅ Cleared: 12 | ❌ Blocked: 1 | 📊 Total: 13
```

This gives instant visibility into expedition progress without opening the Playwright report.

### Artifacts

Two artifacts are uploaded:
- **`playwright-report/`** (14 days) — The full HTML evidence report with screenshots, traces, and timeline
- **`test-results/`** (7 days) — Raw JSON results including `checkpoints.json`

---

## 18. Step-by-Step Usage Guide

### Getting Started

**1. Install dependencies:**
```bash
npm install
npx playwright install --with-deps chromium
```

**2. Configure environment:**
Create `.env.local`:
```
BASE_URL=http://localhost:3000
TEST_EMAIL=test@example.com
TEST_PASSWORD=your-test-password
```

**3. Verify setup:**
```bash
npm test
```

### Starting a New Feature

**Step 1: Survey the terrain**
```
/survey
```
The agent will ask you questions about the feature, identify hazards, and propose approaches.

**Step 2: Chart the journey**
The agent creates a Mermaid diagram in `USER-JOURNEYS.md` with all checkpoints marked ❌.

**Step 3: Mark checkpoints**
The agent extracts checkpoints into a structured list with categories and priorities.

**Step 4: Scout the trail**
```
/scout
```
The agent writes failing Playwright tests for every checkpoint. Uses `npx playwright codegen` for complex flows.

Verify all tests fail:
```bash
npx playwright test --reporter=list
```

**Step 5: Build the trail**
```
/build
```
The agent implements one checkpoint at a time:
```bash
npx playwright test --grep "AUTH-01" --reporter=list  # Watch it FAIL
# Agent writes code...
npx playwright test --grep "AUTH-01" --reporter=list  # Watch it PASS
```

**Step 6: Report the expedition**
```
/report
```
The agent generates the expedition report, updates coverage, and creates the PR.

### Useful Commands During Development

```bash
# Run all E2E tests
npm test

# Run all unit tests
npm run test:unit

# Run BOTH unit + E2E (full verification)
npm run test:all

# Run a single E2E checkpoint
npx playwright test --grep "AUTH-01"

# Run a single unit checkpoint
npx vitest run --testNamePattern "AUTH-U01"

# Unit test watch mode (re-runs on file change)
npm run test:unit:watch

# Debug a failing E2E test (step-through in browser)
npx playwright test --grep "AUTH-01" --debug

# Watch the E2E test run in a visible browser
npm run test:headed

# Record a new test flow
npm run test:codegen

# View the HTML test report
npm run test:report

# View a failure trace (screenshots + timeline + network)
npm run test:trace test-results/<test>/trace.zip

# Update coverage from test results
npm run test:coverage

# Regenerate the trail map
npm run test:generate-map

# Re-run only failed E2E tests
npx playwright test --last-failed

# Check for flaky tests (run 10x)
npx playwright test --grep "AUTH-01" --repeat-each=10
```

### Manual Coverage Updates

If you need to update coverage without running tests:
```bash
npx tsx scripts/update-coverage.ts --status AUTH-01:pass,AUTH-02:fail,AUTH-03:skip
```

---

## 19. How to Extend Pathfinder: Writing New Skills

Pathfinder is designed to grow. The `writing-skills` meta-skill teaches you how to create new skills using the same TDD methodology that Pathfinder enforces for code.

### RED Phase: Observe the Failure

1. Give an agent a task WITHOUT the new skill loaded
2. Watch what goes wrong — Did it skip steps? Write code before tests? Claim completion without evidence?
3. Record the specific failure patterns and rationalizations it used

### GREEN Phase: Write the Skill

Create `skills/<skill-name>/SKILL.md` with this structure:

```markdown
---
name: skill-name
description: >
  One-line description of when this skill activates.
---

# Skill Name

**Goal:** What this skill achieves.
**Prerequisite:** What must be true before this skill activates.
**Territory:** What files/directories this skill operates on.

## The Process
[Step-by-step instructions with CLI commands]

## Anti-Rationalization
[Table of rationalizations and counters]
```

### REFACTOR Phase: Close Loopholes

1. Run the scenario again WITH the skill loaded
2. If the agent finds a new way to skip → add a counter
3. If the skill is too verbose → simplify without losing enforcement
4. If agents ignore a section → restructure for scannability

### Key Principles for Skill Writing

- **Specific over generic** — Address exact failure modes, not abstract advice
- **Commands over prose** — Give copy-pasteable CLI commands, not paragraphs
- **Anti-rationalization is mandatory** — Every skill needs a rationalization table
- **Evidence over claims** — Every verification needs a specific command to run
- **Brevity wins** — Agents have limited context. Every word must earn its place

### Adding the Skill to the Router

Update the skill routing table in `skills/using-pathfinder/SKILL.md`:

```markdown
| Trigger | Skill | When |
|---------|-------|------|
| Your trigger | `pathfinder:your-skill` | When to invoke |
```

---

## 20. Inspirations and Credits

### obra/superpowers

The composable skills architecture, SessionStart hooks, "The Rule" (1% chance → MUST invoke), anti-rationalization tables, slash commands, fresh context dispatch, two-stage review, and verification-before-completion all come from Jesse Vincent's [superpowers](https://github.com/obra/superpowers) project. Superpowers pioneered the idea that AI agent behavior can be *encoded as composable skill files* rather than monolithic instruction documents.

### Playwright

Microsoft's [Playwright](https://playwright.dev) provides the entire testing platform: the test runner, browser automation, auto-waiting, network mocking, codegen, trace viewer, HTML reporter, and the custom fixture/reporter APIs that Pathfinder extends.

### Test-Driven Development

The methodology itself comes from Kent Beck's TDD practice. Pathfinder doesn't invent TDD — it *enforces* TDD on AI agents that would otherwise skip it. The Iron Law ("NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST") is Beck's core principle, and the RED-GREEN-REFACTOR cycle is TDD's heartbeat.

---

## Repository Structure

```
Pathfinder/
├── AGENTS.md                          # Slim agent instructions (points to skills/)
├── README.md                          # Project overview with architecture diagram
├── SKILL.md                           # Project metadata (v0.2.0)
├── PROPOSAL.md                        # Improvement proposal with full analysis
├── package.json                       # npm scripts for all CLI commands
├── tsconfig.json                      # TypeScript strict configuration
├── playwright.config.ts               # 4 reporters, auth project, evidence collection
├── vitest.config.ts                   # Unit test configuration (Vitest)
├── .gitignore                         # node_modules, .auth, test-results, etc.
│
├── skills/                            # 12 composable skill files
│   ├── using-pathfinder/SKILL.md      # Meta-skill (auto-loaded via SessionStart)
│   ├── surveying/SKILL.md             # Phase 1: Requirements gathering
│   ├── planning/SKILL.md              # Phase 2: Chart map + define checkpoints
│   ├── scouting/SKILL.md              # Phase 3: Write failing tests (E2E + unit)
│   ├── building/SKILL.md              # Phase 4: Implement to pass tests
│   ├── dispatching/SKILL.md           # Phase 5: Multi-agent coordination (optional)
│   ├── reporting/SKILL.md             # Phase 6: Evidence, PR, close expedition
│   ├── unit-testing/SKILL.md          # Cross-cutting: Vitest enforcement
│   ├── git-workflow/SKILL.md          # Cross-cutting: Branches, commits, PRs
│   ├── code-review/SKILL.md           # Cross-cutting: Structured PR review
│   ├── security/SKILL.md              # Cross-cutting: OWASP, input validation
│   └── systematic-debugging/SKILL.md  # Cross-cutting: Root-cause investigation
│
├── hooks/
│   └── hooks.json                     # SessionStart → loads using-pathfinder
│
├── commands/                          # 4 slash commands
│   ├── survey.md                      # /survey → pathfinder:surveying
│   ├── scout.md                       # /scout → pathfinder:scouting
│   ├── build.md                       # /build → pathfinder:building
│   └── report.md                      # /report → pathfinder:reporting
│
├── e2e/                               # Playwright test directory
│   ├── auth.setup.ts                  # Auth project (login + save state)
│   ├── example.spec.ts                # Example test with checkpoint fixture
│   ├── fixtures/
│   │   └── pathfinder.ts              # Custom checkpoint fixture
│   └── reporters/
│       └── pathfinder-reporter.ts     # Custom checkpoint reporter
│
├── scripts/
│   ├── update-coverage.ts             # JSON-based coverage state management
│   └── generate-map.ts                # Generates USER-JOURNEYS.md from state
│
├── templates/                         # Starter templates for new projects
│   ├── user-journeys.md
│   └── test-file.ts
│
├── .github/
│   ├── workflows/pathfinder.yml       # CI pipeline with coverage comments
│   └── PULL_REQUEST_TEMPLATE.md       # Expedition report template
│
└── docs/                              # Reference documentation
    ├── installation.md
    ├── tdd-workflow.md
    ├── journey-format.md
    ├── component-driven.md
    ├── ci-integration.md
    └── writing-skills.md              # Guide for creating new skills
```

---

## Glossary

| Term | Definition |
|------|-----------|
| **Checkpoint** | A specific verifiable point in a user journey, mapped to a Playwright test |
| **Trail Marker** | Visual status indicator (❌🔄✅⚠️⏭️) for a checkpoint |
| **Journey** | A complete user flow through the application (e.g., "Auth Journey") |
| **Trail Map** | Mermaid diagram + checkpoint tables showing all journeys and their status |
| **Scout** | Agent role that writes tests (territory: `e2e/` only) |
| **Builder** | Agent role that implements code (territory: `src/` only) |
| **Expedition** | A complete feature development cycle from survey to report |
| **The Rule** | "If there is even a 1% chance a skill applies, MUST invoke it" |
| **Iron Law** | "No production code without a failing test first" |
| **Fresh Context** | Each dispatched agent starts clean with all necessary information |
| **Anti-Rationalization** | Pre-written counters to excuses agents use to skip steps |
| **Cleared** | A checkpoint whose test is passing (✅) |
| **Scouted** | A checkpoint whose test exists but fails (🔄) — the RED phase |
| **Uncharted** | A checkpoint identified but without a test yet (❌) |

---

*Pathfinder — Marks the trail before others follow.*
