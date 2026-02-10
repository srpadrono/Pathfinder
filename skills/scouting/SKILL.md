---
name: scouting
description: >
  Phase 4: Write failing tests for ALL checkpoints before any implementation.
  Scout the trail using Playwright CLI.
---

# Scouting — Phase 4

**Goal:** Write failing tests for ALL checkpoints before any implementation.

**Prerequisite:** Checkpoints marked (Phase 3 complete).
**Territory:** `e2e/` and `USER-JOURNEYS.md` for E2E tests. `src/**/*.test.ts` for unit tests. Do NOT modify implementation code in `src/`.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Wrote code before the test? Delete it. Start over. No exceptions.

## Write Tests Using Playwright

```typescript
import { test, expect } from './fixtures/pathfinder';

test.describe('Feature Journey', () => {
  test('FEAT-01: Main flow works', async ({ page, checkpoint }) => {
    checkpoint.mark('FEAT-01', 'Main flow works');
    await page.goto('/feature');
    await expect(page.locator('h1')).toBeVisible();
    checkpoint.clear('FEAT-01');
  });
});
```

## Codegen-Assisted Scouting

For complex UI flows, use Playwright's codegen to record interactions:

```bash
# Record happy path
npx playwright codegen --load-storage=.auth/state.json http://localhost:3000/feature

# Record with mobile viewport
npx playwright codegen --viewport-size="375,812" http://localhost:3000/feature
```

1. Start recording
2. Perform the user journey
3. Copy generated test code
4. Refactor into checkpoint format with proper `expect()` assertions
5. Add edge case tests that codegen can't capture

**Codegen captures the HAPPY PATH. The Scout must ALSO write:**
- Error state tests (mock API failures via `page.route`)
- Empty state tests (mock empty responses)
- Edge case tests (boundary values)
- Validation tests (invalid inputs)

## Write Unit Tests (Alongside E2E)

For every function, module, or component that the E2E checkpoint depends on, write co-located unit tests. See `pathfinder:unit-testing` for full details.

```typescript
// src/utils/validate-email.test.ts
import { describe, it, expect } from 'vitest';
import { validateEmail } from './validate-email';

describe('Auth Journey — Unit', () => {
  it('AUTH-U01: validateEmail rejects empty string', () => {
    expect(validateEmail('')).toBe(false);
  });
});
```

Unit checkpoints use the `U` suffix: `AUTH-U01`, `AUTH-U02`, etc.

## Verify RED (Mandatory)

```bash
# E2E tests
npx playwright test e2e/feature.spec.ts --reporter=list

# Unit tests
npx vitest run src/**/feature*.test.ts --reporter=verbose
```

Confirm for BOTH layers:
- Test FAILS (not errors from typos)
- Failure message is the expected one
- Fails because feature is MISSING, not because test is broken

## After Scouting

1. Update diagram markers: ❌ → 🔄
2. Run ALL tests to confirm they FAIL: `npm run test:all`
3. Commit: `"Scout: Mark trail for FEAT-01 through FEAT-05 (E2E + unit)"`

## Anti-Rationalization

| Rationalization | Counter |
|----------------|---------|
| "I'll write tests and code together" | That's not TDD. Scout phase = tests ONLY. |
| "This test is too simple to verify RED" | If you didn't watch it fail, you don't know it tests the right thing. |
| "I'll skip codegen, I know the selectors" | Codegen prevents typos in selectors. Use it for complex flows. |
| "I'll write the error tests later" | Error tests ARE the tests. Write them now. |
| "E2E covers this, no unit test needed" | E2E is slow and tells you something broke. Unit tests tell you what. Write both. |
