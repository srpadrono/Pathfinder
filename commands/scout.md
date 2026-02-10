---
disable-model-invocation: true
---

Invoke the `pathfinder:scouting` skill.

PREREQUISITE: A charted trail map must exist in USER-JOURNEYS.md.
If no map exists, invoke `pathfinder:surveying` first.

Write failing tests for ALL checkpoints before any implementation.

Use Playwright CLI:
- Generate test scaffolding: `npx playwright codegen --load-storage=.auth/state.json <url>`
- Run tests to verify RED: `npx playwright test --grep <checkpoint-id> --reporter=list`
- Verify failure is correct (missing feature, not typo)

After all tests written:
1. Update markers: ❌ → 🔄
2. Run all tests to confirm they ALL fail
3. Commit: "Scout: Mark trail for FEAT-01 through FEAT-XX"
