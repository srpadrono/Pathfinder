---
name: dispatching
description: >
  Cross-cutting: Coordinate Scout and Builder agents efficiently.
  Fresh context dispatch with two-stage review.
---

# Dispatching (Optional)

**Goal:** Coordinate Scout and Builder agents efficiently.

## Fresh Context Principle

Each dispatched agent starts fresh. No context pollution from previous tasks.
Every dispatch includes EVERYTHING the agent needs.

### Hard Rules for Sub-Agent Dispatch

0. **Create a feature branch after Survey is approved and before any Scout work begins** — `git checkout -b feat/expedition-name`.
   ALL work happens on the branch. NEVER commit expedition work to main directly.
   The pre-push hook will block you if you forget.
1. **Paste the FULL skill text** — not a summary, not "follow Pathfinder." Copy-paste the entire
   relevant SKILL.md content into the task. Sub-agents don't have access to your skill files.
2. **Max 3 checkpoints per builder dispatch** — batching more causes shortcuts. If you have 10
   checkpoints, dispatch 4 builder tasks of 2-3 each.
3. **Builder tasks MUST include the verify loop** — the task description must explicitly say:
   "For each checkpoint: run test → verify FAIL → implement → run test → verify PASS → commit."
4. **Scout tasks MUST include both test layers** — "Write E2E tests AND unit tests" not just one.
5. **Every dispatch must reference the gate file** — "Read `.pathfinder/plan.json` for checkpoint definitions."
6. **Report phase completes the expedition** — after Build, run `verify-expedition.sh` to compute the quality score, then create a PR via `gh pr create`. Skipping this means no one can verify your work.

## Scout Dispatch Template

```
You are a SCOUT for the Pathfinder expedition workflow.

YOUR TERRITORY: e2e/ for E2E tests, src/**/*.test.ts for unit tests, and USER-JOURNEYS.md.
FORBIDDEN: Do NOT modify src/ implementation code (only test files).

TASK: Write failing tests for checkpoints FEAT-01 through FEAT-05.

GATE FILE: Read .pathfinder/plan.json for checkpoint definitions.

TRAIL MAP:
[paste relevant section of USER-JOURNEYS.md]

CHECKPOINT DETAILS:
- FEAT-01: [description + acceptance criteria]
- FEAT-02: [description + acceptance criteria]
- FEAT-03: [description + acceptance criteria]

=== BOTH TEST LAYERS REQUIRED ===

For EACH checkpoint, write:
1. An E2E test in e2e/feature.spec.ts (tests user-visible behavior)
2. A unit test in the appropriate src/**/*.test.ts (tests internal logic)

Unit checkpoint naming: FEAT-U01, FEAT-U02, etc.

E2E TEST FILE: e2e/feature.spec.ts
UNIT TEST FILES: [list expected locations, e.g. src/utils/feature.test.ts]

TEST COMMANDS:
  npx playwright test e2e/feature.spec.ts --reporter=list
  npx vitest run src/**/feature*.test.ts --reporter=verbose

EXPECTED RESULT: ALL tests FAIL (feature not implemented yet)

=== VERIFY RED ===

After writing all tests, run both commands above. Paste the output showing failures.
Tests must FAIL because the feature is MISSING, not because of typos or import errors.

WHEN DONE:
1. Commit: "Scout: Mark trail for FEAT-01 through FEAT-05 (E2E + unit)"
2. Update USER-JOURNEYS.md markers: ❌ → 🔄
3. Create .pathfinder/scout.json with checkpoint list and test file paths
4. Report: List all checkpoints with E2E + unit test descriptions
```

## Builder Dispatch Template

**Max 3 checkpoints per dispatch. No exceptions.**

```
You are a BUILDER for the Pathfinder expedition workflow.

YOUR TERRITORY: src/ and implementation code ONLY.
FORBIDDEN: Do NOT modify test assertions in e2e/ or unit tests.

TASK: Clear trail for checkpoints FEAT-01 through FEAT-03.

GATE FILE: Read .pathfinder/plan.json for checkpoint definitions.

TRAIL MAP:
[paste relevant section of USER-JOURNEYS.md]

E2E TESTS: e2e/feature.spec.ts
UNIT TESTS: [list the unit test files]

=== CRITICAL: THE BUILD LOOP (one checkpoint at a time) ===

For FEAT-01:
1. Run unit test: npx vitest run --testNamePattern "FEAT-U01"
   → MUST see FAIL. Paste the failure output.
2. Run E2E test: npx playwright test --grep "FEAT-01" --reporter=list
   → MUST see FAIL. Paste the failure output.
3. Write MINIMAL code to pass both tests.
4. Run unit test: npx vitest run --testNamePattern "FEAT-U01"
   → MUST see PASS. Paste the pass output.
5. Run E2E test: npx playwright test --grep "FEAT-01" --reporter=list
   → MUST see PASS. Paste the pass output.
6. Run full suite: npm run test:all → Verify 0 regressions.
7. Commit: "Builder: Clear FEAT-01"
8. Update marker in USER-JOURNEYS.md: 🔄 → ✅

Then repeat for FEAT-02 and FEAT-03.

=== DEPENDENCY CHECK (v0.4.0 — before each checkpoint) ===

Before working on any checkpoint, run:
  bash scripts/pathfinder-check-deps.sh <CHECKPOINT-ID>

If it says "Blocked" → skip this checkpoint and move to the next unblocked one.
Report which checkpoints were blocked and why.

=== TASK FILE UPDATES (after each checkpoint) ===

After clearing a checkpoint, update its task file per references/task-tracking.md.
  git add .pathfinder/tasks/<ID>.json

=== EVIDENCE REQUIRED ===

For each checkpoint, include an evidence block in your report:

<!-- EVIDENCE:FEAT-01 -->
- Unit test FAIL output: [paste]
- Unit test PASS output: [paste]
- E2E test FAIL output: [paste]
- E2E test PASS output: [paste]
- Full suite: [paste summary line showing 0 failures]
<!-- /EVIDENCE:FEAT-01 -->

WHEN DONE:
1. Run full suite: npm run test:all
2. Verify 0 failures across BOTH layers
3. Report: List all checkpoints with evidence blocks
```

## Two-Stage Expedition Review

After each Builder completes a checkpoint:

### Stage 1: Trail Compliance Review

A reviewer verifies:
- [ ] Implementation matches the checkpoint description exactly
- [ ] No extra features beyond what the checkpoint requires (YAGNI)
- [ ] Test was written BEFORE implementation (check git log)
- [ ] Screenshot evidence matches expected behavior
- [ ] Marker correctly updated (🔄 → ✅)

If trail compliance fails → Builder fixes → Re-review Stage 1.

### Stage 2: Code Quality Review

Only runs after Stage 1 passes:
- [ ] Minimal code — simplest solution that passes the test
- [ ] No console errors or warnings
- [ ] No hardcoded values that should be configurable
- [ ] Error handling for the checkpoint's edge cases
- [ ] Code matches project conventions

If quality fails → Builder fixes → Re-review Stage 2 only.

### Review Is a Loop

Reviews repeat until both stages pass. No exceptions.

## Handoff Protocol

**Scout → Builder:**
```
@builder — Trail marked for FEAT-01 through FEAT-05.
Tests in e2e/feature.spec.ts. Map in USER-JOURNEYS.md.
Run: npx playwright test e2e/feature.spec.ts
All tests should FAIL (expected).
```

**Builder → Scout:**
```
@scout — Trail cleared. All checkpoints passing.
Evidence: test-results/ and playwright-report/
Ready for expedition report.
```

## Single-Agent Mode

When one agent handles both roles:

1. **Scout phase first** — Write ALL tests, verify they FAIL
2. **Commit scout work** — Save tests and map
3. **Switch to Builder** — Implement without changing tests
4. **If tests need fixing** — Switch back to Scout explicitly

Never blur the boundary. Complete one role before switching.
