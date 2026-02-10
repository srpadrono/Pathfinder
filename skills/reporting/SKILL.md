---
name: reporting
description: >
  Phase 7: Create PR with evidence, trail map, and review checklist.
  Generate the expedition report.
---

# Reporting — Phase 7

**Goal:** Create PR with evidence, map, and review checklist.

**Prerequisite:** All checkpoints ✅ (Phase 5 complete).

## Pre-Report Verification

```bash
# Run full suite
npx playwright test --reporter=list

# Generate HTML report with evidence
npx playwright test --reporter=html

# View the report
npx playwright show-report

# Verify checkpoints.json is up to date
cat test-results/checkpoints.json
```

## Pre-Review Checklist

Before requesting review, verify ALL:

- [ ] All tests pass (`npx playwright test` = 0 failures)
- [ ] Trail map updated (all checkpoints ✅)
- [ ] Screenshots captured (in `test-results/`)
- [ ] No console errors or warnings
- [ ] Code matches spec
- [ ] YAGNI applied (no extra features)
- [ ] Coverage synced (`npm run test:coverage`)

## PR Structure

Use the expedition report template:

1. **Trail Map** — Final Mermaid diagram (all ✅)
2. **Checkpoint Table** — ID, description, status, evidence link
3. **Edge Cases Covered** — Matrix from Phase 3
4. **Evidence** — Screenshot links from `playwright-report/`
5. **Expedition Log** — What was built, decisions made, issues encountered

## Issue Severity

| Severity | Action | Examples |
|----------|--------|----------|
| **Critical** | Block merge, fix immediately | Tests fail, security issue, data loss |
| **Important** | Fix before merge | Missing error handling, poor UX |
| **Minor** | Note for later | Magic numbers, naming nitpicks |

Critical issues block progress. No exceptions.
