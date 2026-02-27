---
disable-model-invocation: true
---

Invoke the `pathfinder:reporting` skill.

PREREQUISITE: All checkpoints must be ✅.
If any checkpoint is not cleared, invoke `pathfinder:building` first.

Generate expedition report:

1. Run full test suite: `npx playwright test --reporter=list`
2. Generate HTML report: `npx playwright test --reporter=html`
3. View report: `npx playwright show-report`
4. Update coverage: `npm run test:coverage`
5. Generate trail map: `npm run test:generate-map`
6. Collect evidence from `test-results/` and `playwright-report/`
7. Create PR using .github/PULL_REQUEST_TEMPLATE.md
