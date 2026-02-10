---
name: reporting
description: >
  Phase 7: Create PR with evidence, trail map, and review checklist.
  Generate the expedition report. See git-workflow for branch/PR conventions.
---

# Reporting — Phase 7

**Goal:** Create PR with evidence, map, and review checklist.

**Prerequisite:** All checkpoints ✅ (Phase 5 complete). Branch created per `pathfinder:git-workflow`.

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

# Verify checkpoints.json is up to date
cat test-results/checkpoints.json
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

# 4. Or without gh CLI — use the URL git prints after push
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
