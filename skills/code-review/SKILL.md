---
name: code-review
description: >
  Structured code review for PRs and expedition reports.
  Verify trail compliance, code quality, and security before merge.
---

# Code Review

**Goal:** Review code changes with a structured checklist. No rubber-stamping.

**When:** Reviewing a PR, expedition report, or another agent's work.

## The Review Process

### 1. Understand the Expedition

Before reading code, understand what was built:

```bash
# What changed?
git diff main...HEAD --stat

# What checkpoints were targeted?
cat USER-JOURNEYS.md

# What do the tests verify?
npx playwright test --list
```

### 2. Run the Tests Yourself

Never trust "all tests pass" claims. Run them:

```bash
npm run test:all
```

If they don't pass on your machine, the PR is not ready.

### 3. Trail Compliance Review

| Check | How to Verify |
|-------|--------------|
| Tests written BEFORE implementation? | `git log --oneline` — Scout commits before Builder commits |
| Every checkpoint has a test? | Compare `USER-JOURNEYS.md` checkpoints to `e2e/*.spec.ts` test titles |
| No extra features beyond checkpoints? | `git diff main...HEAD` — look for code not covered by any test |
| Markers correctly updated? | All targeted checkpoints show ✅ in trail map |
| Evidence matches behavior? | Open `playwright-report/` and verify screenshots |

### Task File Review (v0.4.0)

| Check | How to Verify |
|-------|--------------|
| Task files exist? | `ls .pathfinder/tasks/*.json` — one per checkpoint |
| Task statuses correct? | Each task file shows `"status": "verified"` or `"green"` |
| State file consistent? | `cat .pathfinder/state.json` — phase and counts match reality |
| Evidence filled? | Each task file has `evidence.green` with test output |

Cross-reference: See `pathfinder:dispatching` for the two-stage review process (Trail Compliance → Code Quality).

### 4. Code Quality Review

| Check | What to Look For |
|-------|-----------------|
| Minimal code? | Could the same test pass with less code? |
| No hardcoded values? | URLs, credentials, magic numbers in `src/` |
| Error handling? | What happens when the API fails? Network drops? |
| No console.log left behind? | Search for `console.log` in `src/` |
| Naming clarity? | Can you understand the code without comments? |
| No dead code? | Unused imports, unreachable branches, commented-out code |

### 5. Security Review

Cross-reference with `pathfinder:security` for the full checklist:

- [ ] No secrets in code (API keys, passwords, tokens)
- [ ] User input is validated/sanitized
- [ ] No raw SQL or unescaped HTML
- [ ] Auth checks on protected routes
- [ ] No sensitive data in logs or error messages

## Feedback Format

Structure review comments by severity:

```
🔴 CRITICAL: [Must fix before merge]
Description and suggested fix.

🟡 IMPORTANT: [Should fix before merge]
Description and suggested fix.

🟢 MINOR: [Note for future]
Description.
```

## What NOT to Do in Reviews

| Anti-Pattern | Why It's Wrong |
|-------------|---------------|
| Approve without running tests | You're trusting claims over evidence |
| Only review the latest commit | The PR includes ALL commits. Review them all. |
| Nitpick style while ignoring logic | Style is minor. Logic bugs are critical. Prioritize. |
| Rewrite the code in your review | Suggest changes, don't impose rewrites. The builder owns the code. |
| Block on personal preference | If the tests pass and it matches the spec, preference is not a blocker. |

## Anti-Rationalization

| Rationalization | Counter |
|----------------|---------|
| "The tests pass, so the code is fine" | Tests don't catch everything. Review the logic, not just the green checkmarks. |
| "I trust this developer/agent" | Trust is not a review strategy. Read the code. |
| "This PR is too large to review properly" | Then it should have been smaller. Request it be split. |
| "I'll do a thorough review later" | Later never comes. Review now or request changes. |
