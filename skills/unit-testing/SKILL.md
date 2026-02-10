---
name: unit-testing
description: >
  Unit test enforcement for the Pathfinder workflow.
  Complements E2E scouting with fine-grained component/function tests using Vitest.
---

# Unit Testing

**Goal:** Enforce unit tests for individual functions, components, and modules alongside E2E tests.

**When:** Any time production code is written in `src/`. Unit tests verify internal correctness; E2E tests verify user-facing behavior. Both are required.

## Responsibility

| Role | Unit Tests | E2E Tests |
|------|-----------|-----------|
| **Scout** | Writes failing unit tests in `src/**/*.test.ts` | Writes failing E2E tests in `e2e/` |
| **Builder** | Makes unit tests pass | Makes E2E tests pass |

The Scout writes BOTH types of tests before the Builder writes any code. The Builder must pass BOTH before claiming a checkpoint is cleared.

## The Iron Law (Extended)

```
NO PRODUCTION CODE WITHOUT FAILING TESTS FIRST — BOTH UNIT AND E2E
```

- E2E tests verify the USER sees the right thing (Playwright)
- Unit tests verify the CODE does the right thing (Vitest)
- One does not replace the other. Both are mandatory.

## When to Write Unit Tests

| Scenario | Unit Test Required? | Why |
|----------|-------------------|-----|
| Pure function (validation, formatting, calculation) | **Yes — always** | Fastest feedback, easiest to isolate |
| API route handler | **Yes** | Test request/response without browser overhead |
| State management (store, reducer, context) | **Yes** | Verify state transitions independently |
| Utility/helper module | **Yes** | Prevent silent regressions |
| Component rendering logic | **Yes** | Test props → output without full browser |
| Component user interaction | **E2E preferred** | Playwright tests real browser behavior |
| Full user journey (login → dashboard) | **E2E only** | Cross-page flows need a real browser |

## Checkpoint Naming Convention

Unit test checkpoints use the same journey prefix with a `U` suffix:

| Type | Format | Example |
|------|--------|---------|
| E2E checkpoint | `AUTH-01` | `AUTH-01: Login redirects to dashboard` |
| Unit checkpoint | `AUTH-U01` | `AUTH-U01: validateEmail rejects empty string` |

This keeps unit and E2E checkpoints in the same trail map while making them distinguishable.

## Writing Unit Tests

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

  it('AUTH-U04: validateEmail rejects whitespace-only', () => {
    expect(validateEmail('   ')).toBe(false);
  });
});
```

## Verify RED (Mandatory)

```bash
# Run specific unit checkpoint
npx vitest run --reporter=verbose --testNamePattern "AUTH-U01"

# Run all unit tests for a journey
npx vitest run src/**/auth*.test.ts --reporter=verbose

# Run ALL unit tests
npx vitest run
```

Confirm:
- Test FAILS (not errors from typos)
- Failure message is the expected one
- Fails because function is MISSING or UNIMPLEMENTED, not because test is broken

## Verify GREEN

```bash
# Run the specific test
npx vitest run --testNamePattern "AUTH-U01"

# Run all unit tests — no regressions
npx vitest run

# Run BOTH unit and E2E — full verification
npm run test:all
```

## The Full Verification Loop

For each checkpoint, the Builder must pass BOTH layers:

```bash
# 1. Unit test — watch it FAIL
npx vitest run --testNamePattern "AUTH-U01"

# 2. Write minimal code

# 3. Unit test — watch it PASS
npx vitest run --testNamePattern "AUTH-U01"

# 4. E2E test — verify it also works in browser
npx playwright test --grep "AUTH-01"

# 5. Full suite — no regressions in either layer
npm run test:all
```

## Watch Mode for Development

```bash
# Interactive watch mode — re-runs on file change
npx vitest

# Watch specific files
npx vitest src/utils/validate-email.test.ts
```

Watch mode is useful during the BUILD phase for rapid RED-GREEN cycles on unit tests. It is NOT a substitute for running the full suite before claiming cleared.

## Co-Located Test Files

Unit tests live NEXT TO the code they test:

```
src/
├── utils/
│   ├── validate-email.ts           ← Implementation
│   └── validate-email.test.ts      ← Unit test
├── hooks/
│   ├── use-auth.ts
│   └── use-auth.test.ts
├── api/
│   ├── login.ts
│   └── login.test.ts
└── components/
    ├── LoginForm.tsx
    └── LoginForm.test.tsx
```

Co-location makes it obvious when a file is missing its tests. If you see a `.ts` file without a `.test.ts` beside it, that's a red flag.

## Anti-Rationalization

| Rationalization | Counter |
|----------------|---------|
| "E2E tests cover everything" | E2E tests are slow and coarse. A failing E2E test tells you SOMETHING broke — a failing unit test tells you WHAT broke. |
| "This function is too simple to unit test" | Simple functions have edge cases. `validateEmail('')` — did you handle that? |
| "Unit tests are redundant with E2E" | They test different things. E2E: user sees correct UI. Unit: function returns correct value. Both can pass while the other fails. |
| "I'll add unit tests later" | Later never comes. The function is fresh in your mind NOW. Write it now. |
| "Mocking is too complex" | If you need complex mocks, your code has too many dependencies. Simplify the code first. |
| "The component is just a wrapper" | Wrappers have prop-passing bugs, default value bugs, and conditional rendering bugs. Test them. |

## Red Flags — Unit Testing Abandoned

- `src/` has `.ts` files without corresponding `.test.ts` files
- Unit tests only test the happy path (no edge cases)
- Unit tests mock everything (testing mocks, not code)
- Unit tests were written AFTER implementation (biased)
- `npm run test:unit` is not part of the verification loop
