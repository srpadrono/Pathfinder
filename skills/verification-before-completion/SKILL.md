---
name: verification-before-completion
description: >
  Evidence-based verification before claiming any task is complete.
  No self-certifying. Evidence over claims.
---

# Verification Before Completion

## The Rule

NEVER claim a checkpoint is cleared without evidence.
NEVER claim all tests pass without running them.
NEVER mark 🔄 → ✅ without a passing test run.

## Required Evidence Per Claim

| Claim | Required Evidence |
|-------|------------------|
| "Test is written" | Show the test code + show it FAILS with expected message |
| "Checkpoint cleared" | Show `npx playwright test --grep "FEAT-XX"` output with PASS |
| "All tests pass" | Show `npx playwright test` full output with 0 failures |
| "No regressions" | Show full suite run, not just the new test |
| "Trail map updated" | Show the diff of USER-JOURNEYS.md with updated markers |
| "PR ready" | Show pre-review checklist with all items checked |

## Verification Commands

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

# Check checkpoint results
cat test-results/checkpoints.json
```

## Anti-Rationalization

| Rationalization | Counter |
|----------------|---------|
| "I'm confident it works" | Confidence is not evidence. Run the test. |
| "I tested it manually" | Manual is not automated. Run `npx playwright test`. |
| "The previous test was similar" | Similar is not identical. Run THIS test. |
| "It's just a small change" | Small changes cause big regressions. Run the suite. |
| "I already ran it earlier" | State changes. Run it NOW. |
| "The CI will catch it" | CI is a safety net, not a substitute. Verify locally first. |
