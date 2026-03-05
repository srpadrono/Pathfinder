---
name: building
description: >
  Phase 4: Implement minimal code to pass each test, one at a time.
  Follow the marked trail using Playwright CLI for verification.
---

# Building — Phase 4

**Goal:** Implement minimal code to pass each test, one at a time.

**Prerequisite:** All checkpoint tests exist and FAIL (Phase 3 complete).
**Territory:** `src/` and implementation code ONLY. Do NOT modify test assertions.

## Gate Check (Mandatory)

Before doing ANYTHING in this phase:

```bash
cat .pathfinder/scout.json
```

If this file doesn't exist or `status` is not `"complete"` → **STOP. Run the Scouting phase first.**
If `allTestsFail` is not `true` → **STOP. Tests should fail before building.**
Read the checkpoint list and test file paths from this file.

## Dependency Check

Before working on any checkpoint, verify its dependencies are satisfied:

```bash
bash scripts/pathfinder-check-deps.sh FEAT-01
```

If it says "Blocked", skip this checkpoint and move to the next unblocked one.

## Update Task Files

After clearing each checkpoint, update its task file from `red` to `green` and record evidence.
See `references/task-tracking.md` for the update procedure.

The post-commit hook auto-updates `state.json` checkpoint counts.

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
- [ ] Evidence block written (see below)

```bash
# Verify no regressions — BOTH layers
npm run test:all
```

## Structured Evidence Blocks

For each checkpoint, write an evidence block. These are machine-grepable and
the Reporting phase will verify they exist for every checkpoint.

```markdown
<!-- EVIDENCE:FEAT-01 -->
**Status:** ✅ Cleared
**Unit FAIL:** `FAIL src/utils/feature.test.ts > FEAT-U01 (expected X to be Y)`
**Unit PASS:** `PASS src/utils/feature.test.ts > FEAT-U01 (2ms)`
**E2E FAIL:** `FAIL e2e/feature.spec.ts > FEAT-01: Main flow works (timeout)`
**E2E PASS:** `PASS e2e/feature.spec.ts > FEAT-01: Main flow works (1.2s)`
**Full suite:** `Tests: 150 passed, 0 failed`
<!-- /EVIDENCE:FEAT-01 -->
```

Write evidence blocks in the PR description or in `.pathfinder/tasks/FEAT-XX.json`
(the `evidence.green` field). The Reporting phase verifies evidence exists for every
checkpoint — without test output, the checkpoint isn't cleared.

## After All Checkpoints Cleared

Create the build gate file:

```bash
cat > .pathfinder/build.json << 'EOF'
{
  "phase": "build",
  "status": "complete",
  "timestamp": "<ISO-8601>",
  "checkpointsCleared": ["FEAT-01", "FEAT-02", "FEAT-03"],
  "fullSuitePass": true,
  "testOutput": "<paste summary line: X passed, 0 failed>"
}
EOF
git add .pathfinder/build.json
git commit -m "Builder: All checkpoints cleared"
```

**The Reporting phase will refuse to proceed without `.pathfinder/build.json`.**

## If Tests Need Fixing

**STOP.** You're back in Scout mode.

1. Explicitly announce: "Entering Scout mode to fix test"
2. Fix the test assertion
3. Watch it fail correctly
4. Switch back: "Entering Builder mode"
5. Continue implementation

Never blur the Scout/Builder boundary.

