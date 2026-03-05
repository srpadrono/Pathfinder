---
name: reporting
description: >
  Phase 5: Verify evidence, create PR, and close the expedition.
  No self-certifying. Evidence over claims.
---

# Reporting — Phase 5

**Goal:** Verify all claims with evidence, create PR, close the expedition.

**Prerequisite:** All checkpoints ✅ (Phase 4 complete). Branch created per `pathfinder:git-workflow`.

## Gate Check (Mandatory)

Before doing ANYTHING in this phase, verify ALL gate files exist:

```bash
cat .pathfinder/survey.json  # status: approved
cat .pathfinder/plan.json    # status: approved
cat .pathfinder/scout.json   # status: complete
cat .pathfinder/build.json   # status: complete
```

If ANY gate file is missing → **STOP. A phase was skipped.** Go back to the earliest missing phase.
Do not create gate files retroactively. Do not proceed without the full chain.

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

### 1. Verify Gate Files Exist

```bash
# ALL gate files must exist and show "approved"/"complete"
cat .pathfinder/survey.json   # status: approved
cat .pathfinder/plan.json     # status: approved, lists checkpoints
cat .pathfinder/scout.json    # status: complete, lists test files
cat .pathfinder/build.json    # status: complete, all checkpoints cleared
```

If ANY gate file is missing → STOP. Go back to the missing phase.

### 2. Verify Evidence Blocks

For every checkpoint in `.pathfinder/plan.json`, grep for its evidence block:

```bash
# Every checkpoint MUST have an evidence block somewhere in the repo or build log
# Evidence blocks follow this pattern:
grep -r "EVIDENCE:FEAT-" . --include="*.md" | grep -c "Status.*Cleared"
```

If any checkpoint lacks an evidence block → STOP. The Builder skipped verification.

### 3. Run Full Test Suite

```bash
# Run BOTH test layers — this is the final proof
npm run test:all

# Generate HTML report with evidence
npx playwright test --reporter=html

# View the report
npx playwright show-report
```

**You MUST paste the full output** of `npm run test:all` showing pass/fail counts.
A summary like "all tests pass" is NOT acceptable. Paste the actual output.

### 4. Verification & Quality Score

Before creating the PR, run the verification script:

```bash
bash scripts/verify-expedition.sh
```

This produces `.pathfinder/report.json` with a 0-100 quality score.
See `references/task-tracking.md` for scoring criteria and thresholds.

If score is below 70, fix the issues and re-run.

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
git push origin feat/<journey-name>

# 3. Create PR with GitHub CLI
gh pr create \
  --base main \
  --head feat/<journey-name> \
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

