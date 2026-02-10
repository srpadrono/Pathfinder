---
name: reporting
description: >
  Phase 6: Verify evidence, create PR, and close the expedition.
  No self-certifying. Evidence over claims.
---

# Reporting — Phase 6

**Goal:** Verify all claims with evidence, create PR, close the expedition.

**Prerequisite:** All checkpoints ✅ (Phase 4 complete). Branch created per `pathfinder:git-workflow`.

## Evidence Over Claims

NEVER claim a checkpoint is cleared without evidence.
NEVER claim all tests pass without running them.
NEVER mark 🔄 → ✅ without a passing test run.

### Required Evidence Per Claim

| Claim | Required Evidence |
|-------|------------------|
| "Test is written" | Show the test code + show it FAILS with expected message |
| "Checkpoint cleared" | Show `npx playwright test --grep "FEAT-XX"` output with PASS |
| "Unit tests pass" | Show `npx vitest run` output with 0 failures |
| "All tests pass" | Show `npm run test:all` full output with 0 failures |
| "No regressions" | Show full suite run, not just the new test |
| "Trail map updated" | Show the diff of USER-JOURNEYS.md with updated markers |
| "PR ready" | Show pre-review checklist with all items checked |

## Pre-Report Verification

```bash
# Run BOTH test layers
npm run test:all

# Generate HTML report with evidence
npx playwright test --reporter=html

# View the report
npx playwright show-report

# Update coverage and trail map
npm run test:coverage
npm run test:generate-map
```

## Pre-Review Checklist

Before requesting review, verify ALL:

- [ ] All tests pass — both layers (`npm run test:all` = 0 failures)
- [ ] Trail map updated (all checkpoints ✅)
- [ ] Screenshots captured (in `test-results/`)
- [ ] No console errors or warnings
- [ ] Code matches spec
- [ ] YAGNI applied (no extra features)
- [ ] Coverage synced (`npm run test:coverage`)
- [ ] Commit history follows Scout → Builder order
- [ ] No secrets or `.env` files committed (`git diff --name-only main..HEAD`)

## Create the PR

See `pathfinder:git-workflow` for full branching details. Quick reference:

```bash
# 1. Commit final state (coverage + trail map)
git add USER-JOURNEYS.md checkpoints.json
git commit -m "Report: Expedition complete for <journey>"

# 2. Push expedition branch
git push origin expedition/<journey-name>

# 3. Create PR with GitHub CLI
gh pr create \
  --base main \
  --head expedition/<journey-name> \
  --title "Expedition: <Journey Name> (<checkpoint-range>)" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md
```

## PR Structure

Use the expedition report template (`.github/PULL_REQUEST_TEMPLATE.md`):

1. **Summary** — One-line description of what trail was cleared
2. **Trail Map** — Final Mermaid diagram (all ✅)
3. **Checkpoint Table** — ID, description, status, evidence link
4. **Coverage** — Total, cleared, blocked, percentage
5. **Expedition Log** — Scout phase checklist + Builder phase checklist
6. **Evidence** — Links to `playwright-report/`, `test-results/`, `checkpoints.json`
7. **Test Commands** — How to reproduce locally (`npm run test:all`)

## After PR is Created

- [ ] Request review from team
- [ ] Respond to review feedback
- [ ] Fix critical/important issues (keep on expedition branch)
- [ ] Re-run `npm run test:all` after each fix
- [ ] Merge only when both review stages pass (see `pathfinder:dispatching`)

## Issue Severity

| Severity | Action | Examples |
|----------|--------|----------|
| **Critical** | Block merge, fix immediately | Tests fail, security issue, data loss |
| **Important** | Fix before merge | Missing error handling, poor UX |
| **Minor** | Note for later | Magic numbers, naming nitpicks |

Critical issues block progress. No exceptions.

## Anti-Rationalization

| Rationalization | Counter |
|----------------|---------|
| "I'm confident it works" | Confidence is not evidence. Run the test. |
| "I tested it manually" | Manual is not automated. Run `npm run test:all`. |
| "The CI will catch it" | CI is a safety net, not a substitute. Verify locally first. |
| "It's just a small change" | Small changes cause big regressions. Run the suite. |
