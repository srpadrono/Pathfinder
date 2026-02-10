---
name: dispatching
description: >
  Phase 5: Coordinate Scout and Builder agents efficiently.
  Fresh context dispatch with two-stage review.
---

# Dispatching — Phase 5 (Optional)

**Goal:** Coordinate Scout and Builder agents efficiently.

## Fresh Context Principle

Each dispatched agent starts fresh. No context pollution from previous tasks.
Every dispatch includes EVERYTHING the agent needs.

## Scout Dispatch Template

```
You are a SCOUT for the Pathfinder expedition workflow.

YOUR TERRITORY: e2e/ and USER-JOURNEYS.md ONLY.
FORBIDDEN: Do NOT modify src/ or any implementation code.

TASK: Write failing tests for checkpoints FEAT-01 through FEAT-05.

TRAIL MAP:
[paste relevant section of USER-JOURNEYS.md]

CHECKPOINT DETAILS:
- FEAT-01: [description + acceptance criteria]
- FEAT-02: [description + acceptance criteria]
- FEAT-03: [description + acceptance criteria]

TEST FILE: e2e/feature.spec.ts
TEST COMMAND: npx playwright test e2e/feature.spec.ts --reporter=list
EXPECTED RESULT: All tests FAIL (feature not implemented yet)

WHEN DONE:
1. Commit: "Scout: Mark trail for FEAT-01 through FEAT-05"
2. Update USER-JOURNEYS.md markers: ❌ → 🔄
3. Report: List all checkpoints with their test descriptions
```

## Builder Dispatch Template

```
You are a BUILDER for the Pathfinder expedition workflow.

YOUR TERRITORY: src/ and implementation code ONLY.
FORBIDDEN: Do NOT modify test assertions in e2e/.

TASK: Clear trail for checkpoints FEAT-01 through FEAT-05.

TRAIL MAP:
[paste relevant section of USER-JOURNEYS.md]

TESTS: e2e/feature.spec.ts

FOR EACH CHECKPOINT:
1. Run: npx playwright test --grep "FEAT-XX" --reporter=list
2. Verify it FAILS (expected)
3. Write minimal code to pass
4. Run: npx playwright test --grep "FEAT-XX" --reporter=list
5. Verify it PASSES
6. Commit: "Builder: Clear FEAT-XX"
7. Update marker: 🔄 → ✅

WHEN DONE:
1. Run full suite: npx playwright test --reporter=list
2. Verify 0 failures
3. Report: List all checkpoints with pass/fail and duration
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
