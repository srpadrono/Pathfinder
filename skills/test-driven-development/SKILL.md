---
name: test-driven-development
description: >
  Core TDD enforcement for the Pathfinder workflow.
  RED-GREEN-REFACTOR cycle with anti-rationalization guards.
---

# Test-Driven Development

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

This applies universally:
- New features
- Bug fixes
- Refactoring that changes behavior
- Any code that will run in production

## RED-GREEN-REFACTOR

```
RED → Verify RED → GREEN → Verify GREEN → REFACTOR → Repeat
```

### RED — Write Failing Test

```typescript
import { test, expect } from './fixtures/pathfinder';

test('FEAT-01: Main flow works', async ({ page, checkpoint }) => {
  checkpoint.mark('FEAT-01', 'Main flow works');
  await page.goto('/feature');
  await expect(page.locator('h1')).toBeVisible();
  checkpoint.clear('FEAT-01');
});
```

### Verify RED (MANDATORY)

```bash
npx playwright test --grep "FEAT-01" --reporter=list
```

Confirm:
- Test FAILS (not errors)
- Failure message is expected
- Fails because feature is MISSING, not typos

### GREEN — Write Minimal Code

Implement the **simplest code** to make the test pass. Nothing more.

### Verify GREEN

```bash
npx playwright test --grep "FEAT-01" --reporter=list
```

Confirm:
- Test PASSES
- No regressions (`npx playwright test --reporter=list`)
- No console errors

### REFACTOR

Remove duplication, improve naming, extract helpers. Tests must stay green.

## Anti-Rationalization Guide

Agents WILL try to skip TDD. These are the most common rationalizations:

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

## Red Flags — TDD Abandoned

If ANY of these occur, STOP and restart from Scout phase:

- You wrote production code before a test
- A test passed on first run (without implementation)
- You modified a test assertion to make it pass
- You skipped a checkpoint because "it's obvious"
- You're writing tests and code in the same commit
- You rationalized "just this once"

## Testing Anti-Patterns

| Anti-Pattern | Problem | Instead |
|--------------|---------|---------|
| Test passes immediately | Doesn't test new behavior | Ensure it fails first |
| Vague test name | "test1", "it works" | Use checkpoint ID + description |
| Testing mocks not code | Proves nothing | Test real behavior |
| Multiple behaviors per test | Hard to debug | One checkpoint per test |
| Testing implementation details | Brittle | Test outcomes via `expect()` |
| Manual throw instead of expect | No rich error messages | Use Playwright `expect()` assertions |
