---
disable-model-invocation: true
---

Invoke the `pathfinder:building` skill.

PREREQUISITE: All checkpoint tests must exist and FAIL (🔄 status).
If tests don't exist, invoke `pathfinder:scouting` first.

Implement minimal code to pass each test, ONE AT A TIME.

Use Playwright CLI:
- Run single checkpoint: `npx playwright test --grep "FEAT-01" --reporter=list`
- Run all journey tests: `npx playwright test e2e/<journey>.spec.ts --reporter=list`
- Debug failures: `npx playwright test --grep "FEAT-01" --debug`
- View trace on retry: `npx playwright show-trace test-results/<test>/trace.zip`

After each checkpoint clears:
1. Update markers: 🔄 → ✅
2. Commit: "Builder: Clear FEAT-01"

After ALL checkpoints cleared:
1. Run full suite: `npx playwright test --reporter=list`
2. Verify 0 failures
