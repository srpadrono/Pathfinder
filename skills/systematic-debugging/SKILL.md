---
name: systematic-debugging
description: >
  Root-cause investigation methodology for debugging failures.
  Diagnose before prescribing. Evidence before fixes.
---

# Systematic Debugging

**Trigger:** Something is broken, failing, or behaving unexpectedly.

## The Process

### 1. Reproduce

Before anything else, reproduce the failure:

```bash
# Run the specific failing test
npx playwright test --grep "FEAT-XX" --reporter=list

# Run with trace for detailed timeline
npx playwright test --grep "FEAT-XX" --trace=on

# Run headed to watch it fail
npx playwright test --grep "FEAT-XX" --headed
```

### 2. Isolate

Narrow down the cause:

- Is it ONE test or MANY?
- Does it fail consistently or intermittently (flaky)?
- Does it fail locally AND in CI?
- What changed since it last passed? (`git log`, `git diff`)

### 3. Diagnose

Use Playwright's debugging tools:

```bash
# Step-through debugger
npx playwright test --grep "FEAT-XX" --debug

# View trace with timeline, screenshots, network
npx playwright show-trace test-results/<test>/trace.zip

# Check last failed tests
npx playwright test --last-failed
```

### 4. Fix

Write a test that reproduces the bug FIRST (RED), then fix it (GREEN):

1. Write a test that fails for the same reason as the bug
2. Verify the test fails
3. Fix the root cause (not symptoms)
4. Verify the test passes
5. Verify no regressions

### 5. Verify

```bash
# Run the fixed test
npx playwright test --grep "FEAT-XX" --reporter=list

# Run full suite — no regressions
npx playwright test --reporter=list
```

## Vitest Debugging

For unit test failures, use Vitest's debugging tools:

```bash
# Run specific test with verbose output
npx vitest run --reporter=verbose

# Node inspector (attach Chrome DevTools)
npx vitest --inspect

# Break on first line (attach debugger before tests run)
npx vitest --inspect-brk

# Run a specific test file
npx vitest run src/utils/feature.test.ts --reporter=verbose
```

### Updating Task Files When Fixing Bugs

If a bug fix changes checkpoint behavior, update the relevant task file.
See `references/task-tracking.md` for the update procedure. If status regressed,
set it back to `"red"` until fixed, then `"green"`.

## Anti-Patterns

| Anti-Pattern | Problem | Instead |
|-------------|---------|---------|
| Fix without reproducing | Might fix the wrong thing | Reproduce first |
| Fix symptoms not cause | Bug returns in different form | Find root cause |
| Shotgun debugging | Random changes obscure the real fix | Isolate then fix ONE thing |
| Skip regression check | Fix causes new failures | Always run full suite |
| Delete the failing test | Hides the bug | Fix the code, not the test |

## Flaky Test Protocol

If a test is intermittently failing:

1. Mark with ⚠️ in trail map
2. Run 10x to confirm flakiness: `npx playwright test --grep "FEAT-XX" --repeat-each=10`
3. Check for: timing issues, race conditions, external dependencies
4. Fix the root cause (usually missing waits or test isolation)
5. Run 10x again to confirm fix
6. Update marker: ⚠️ → ✅
