---
name: scouting
description: >
  Phase 3: Write failing tests for ALL checkpoints before any implementation.
  Scout the trail using Playwright and Vitest.
---

# Scouting — Phase 3

**Goal:** Write failing tests for ALL checkpoints before any implementation.

**Prerequisite:** Plan approved with checkpoints (Phase 2 complete).
**Territory:** `e2e/` for E2E tests. `src/**/*.test.ts` for unit tests. Do NOT touch implementation code.

## Gate Check (Mandatory)

Before doing ANYTHING in this phase:

```bash
cat .pathfinder/plan.json
```

If this file doesn't exist or `status` is not `"approved"` → **STOP. Run the Planning phase first.**
Read the checkpoint list from this file. These are the ONLY checkpoints you write tests for.

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

## Update Task Files (v0.4.0)

After writing tests for each checkpoint, update its task file from `planned` → `red`:

```bash
python3 -c "
import json
t = json.load(open('.pathfinder/tasks/FEAT-01.json'))
t['status'] = 'red'
t['tests'] = {
    'e2e': ['e2e/feature.spec.ts'],
    'unit': ['src/utils/feature.test.ts']
}
t['evidence']['red'] = {
    'e2e': '<paste FAIL output>',
    'unit': '<paste FAIL output>',
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
}
json.dump(t, open('.pathfinder/tasks/FEAT-01.json', 'w'), indent=2)
"
```

Update `state.json` phase:
```bash
python3 -c "
import json
s = json.load(open('.pathfinder/state.json'))
s['currentPhase'] = 'scout'
s['phases']['scout'] = {'status': 'in-progress', 'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'}
json.dump(s, open('.pathfinder/state.json', 'w'), indent=2)
"
bash scripts/pathfinder-update-state.sh
```

## After Scouting

1. Update diagram markers: ❌ → 🔄
2. Run ALL tests to confirm they FAIL: `npm run test:all`
3. Create gate file:

```bash
cat > .pathfinder/scout.json << 'EOF'
{
  "phase": "scout",
  "status": "complete",
  "timestamp": "<ISO-8601>",
  "checkpoints": ["FEAT-01", "FEAT-02", "FEAT-03"],
  "e2eTestFiles": ["e2e/feature.spec.ts"],
  "unitTestFiles": ["src/utils/feature.test.ts"],
  "allTestsFail": true
}
EOF
```

4. Commit: `"Scout: Mark trail for FEAT-01 through FEAT-05 (E2E + unit)"`

**The Building phase will refuse to proceed without `.pathfinder/scout.json`.**

## Anti-Rationalization

| Rationalization | Counter |
|----------------|---------|
| "I'll write tests and code together" | That's not TDD. Scout phase = tests ONLY. |
| "This test is too simple to verify RED" | If you didn't watch it fail, you don't know it tests the right thing. |
| "I'll skip codegen, I know the selectors" | Codegen prevents typos in selectors. Use it for complex flows. |
| "I'll write the error tests later" | Error tests ARE the tests. Write them now. |
| "E2E covers this, no unit test needed" | E2E is slow and tells you something broke. Unit tests tell you what. Write both. |
| "This is too simple to test" | Simple code breaks most often. A 1-line regex can have 10 edge cases. Write the test. |
| "I'll add tests after" | Tests-after verify YOUR implementation. Tests-first verify THE REQUIREMENT. Delete the code. |

## Red Flags — TDD Abandoned

If ANY of these occur, STOP and restart the Scout phase:

- You wrote production code before a test
- A test passed on first run (without implementation)
- You modified a test to make it pass
- You skipped a checkpoint because "it's obvious"
- You're writing tests and code in the same commit

## Testing Anti-Patterns

| Anti-Pattern | Instead |
|-------------|---------|
| Test passes immediately | Ensure it fails first — test the NEW requirement |
| Vague test name ("test1", "it works") | Use checkpoint ID + description |
| Testing mocks not code | Test real behavior |
| Multiple behaviors per test | One checkpoint per test |
| Manual throw instead of expect | Use Playwright `expect()` or Vitest `expect()` |
