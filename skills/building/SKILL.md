---
name: building
description: >
  Phase 5: Implement minimal code to pass each test, one at a time.
  Follow the marked trail using Playwright CLI for verification.
---

# Building — Phase 5

**Goal:** Implement minimal code to pass each test, one at a time.

**Prerequisite:** All checkpoint tests exist and FAIL (Phase 4 complete).
**Territory:** `src/` and implementation code ONLY. Do NOT modify test assertions.

## The Build Loop

For each checkpoint:

```bash
# 1. Run unit test — watch it FAIL
npx vitest run --testNamePattern "FEAT-U01"

# 2. Run E2E test — watch it FAIL
npx playwright test --grep "FEAT-01" --reporter=list

# 3. Write MINIMAL code to pass

# 4. Run unit test — watch it PASS
npx vitest run --testNamePattern "FEAT-U01"

# 5. Run E2E test — watch it PASS
npx playwright test --grep "FEAT-01" --reporter=list

# 6. Update marker: 🔄 → ✅

# 7. Commit: "Builder: Clear FEAT-01"
```

## Minimal Code Principle

Write the **simplest code** to make the test pass.

**Good:**
```typescript
function validateEmail(email: string): boolean {
  return email.includes('@');
}
```

**Bad (YAGNI):**
```typescript
function validateEmail(email: string, options?: {
  allowSubdomains?: boolean;
  checkMX?: boolean;
}): boolean { /* ... */ }
```

Don't add features, refactor other code, or "improve" beyond the test.

## Debugging with Playwright CLI

```bash
# Step-through debugging in headed browser
npx playwright test --grep "FEAT-01" --debug

# View trace on failure (auto-captured on retry)
npx playwright show-trace test-results/feature-FEAT-01/trace.zip

# Run headed to see what's happening
npx playwright test --grep "FEAT-01" --headed
```

## Verification Before Claiming Cleared

For EACH checkpoint:
- [ ] Unit test was FAILING before implementation
- [ ] Unit test is PASSING after implementation
- [ ] E2E test was FAILING before implementation
- [ ] E2E test is PASSING after implementation
- [ ] No other tests broke (run full suite — both layers)
- [ ] No console errors or warnings
- [ ] Screenshot evidence captured

```bash
# Verify no regressions — BOTH layers
npm run test:all
```

## If Tests Need Fixing

**STOP.** You're back in Scout mode.

1. Explicitly announce: "Entering Scout mode to fix test"
2. Fix the test assertion
3. Watch it fail correctly
4. Switch back: "Entering Builder mode"
5. Continue implementation

Never blur the Scout/Builder boundary.

## Anti-Rationalization

| Rationalization | Counter |
|----------------|---------|
| "I'll implement multiple checkpoints at once" | One checkpoint at a time. Smaller commits = easier debugging. |
| "The test assertion is wrong, I'll fix it" | You're not a Scout right now. Announce the mode switch. |
| "I need to refactor first" | Refactor AFTER the test passes, not before. |
| "This needs more than minimal code" | If the test passes with less, you're over-engineering. |
