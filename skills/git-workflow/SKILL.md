---
name: git-workflow
description: >
  Branch creation, commit conventions, and PR workflow for Pathfinder expeditions.
  Ensures every expedition has a clean branch, structured commits, and a proper PR.
---

# Git Workflow

**Goal:** Enforce consistent branching, commit conventions, and PR creation across expeditions.

**When:** At the start of every expedition (after Survey, before Scout) and at the end (Reporting phase).

## Branch Strategy

Every expedition gets its own branch. No working directly on `main`.

### Branch Naming Convention

```
<role>/<journey>-<short-description>
```

| Role | Prefix | Example |
|------|--------|---------|
| Scout | `scout/` | `scout/auth-login-flow` |
| Builder | `builder/` | `builder/auth-login-flow` |
| Full expedition (single agent) | `expedition/` | `expedition/auth-login-flow` |
| Bug fix | `fix/` | `fix/auth-token-expiry` |
| Hotfix (critical) | `hotfix/` | `hotfix/auth-session-crash` |

Rules:
- Lowercase, hyphen-separated
- Journey prefix matches checkpoint IDs (`auth` → `AUTH-01`, `AUTH-02`)
- Short and descriptive — no ticket numbers in the branch name unless the team requires it

### When to Create the Branch

Create the branch **after Survey is approved, before Scouting begins**:

```bash
# 1. Make sure you're on latest main
git checkout main
git pull origin main

# 2. Create expedition branch
git checkout -b expedition/auth-login-flow

# 3. Push branch to remote immediately (establishes tracking)
git push -u origin expedition/auth-login-flow
```

Why before scouting? Because the Scout's first commit (tests + trail map) should already be on the expedition branch. Never commit test scaffolding to `main`.

## Commit Conventions

### Commit Message Format

```
<Role>: <Action> <checkpoint-range-or-description>
```

| Phase | Commit Message | Example |
|-------|---------------|---------|
| Survey | `Survey: Chart requirements for <journey>` | `Survey: Chart requirements for auth login` |
| Chart | `Chart: Map <journey> with <N> checkpoints` | `Chart: Map auth journey with 5 checkpoints` |
| Mark | `Mark: Define checkpoints AUTH-01 through AUTH-05` | |
| Scout | `Scout: Mark trail for AUTH-01 through AUTH-05` | |
| Scout (unit) | `Scout: Add unit tests for AUTH-U01 through AUTH-U05` | |
| Build (per checkpoint) | `Builder: Clear AUTH-01` | |
| Build (batch) | `Builder: Clear AUTH-01 through AUTH-03` | |
| Report | `Report: Expedition complete for auth journey` | |
| Fix | `Fix: Resolve flaky AUTH-03 (race condition)` | |

### Commit Rules

1. **One checkpoint per commit during Build phase** — Smaller commits = easier debugging, cleaner `git bisect`
2. **Scout commits tests separately from map** — Map is documentation, tests are code
3. **Never mix Scout and Builder work in one commit** — Keep roles cleanly separated in git history
4. **Commit messages reference checkpoint IDs** — Makes `git log --oneline` a trail map

### Commit Verification

Before every commit:

```bash
# Unit tests pass
npm run test:unit

# E2E tests pass (or expected to fail in Scout phase)
npx playwright test --reporter=list

# No untracked files you didn't intend
git status

# Review what you're committing
git diff --staged
```

## Pull Request Creation

### When to Create the PR

Create the PR **after all checkpoints are ✅ and the expedition report is ready**.

### Step-by-Step PR Creation

```bash
# 1. Make sure all tests pass — BOTH layers
npm run test:all

# 2. Update coverage and generate trail map
npm run test:coverage
npm run test:generate-map

# 3. Commit final state
git add USER-JOURNEYS.md checkpoints.json
git commit -m "Report: Expedition complete for auth journey"

# 4. Push all commits
git push origin expedition/auth-login-flow

# 5. Create PR using GitHub CLI
gh pr create \
  --base main \
  --head expedition/auth-login-flow \
  --title "Expedition: Auth Login Flow (AUTH-01 through AUTH-05)" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md
```

### PR Without GitHub CLI

If `gh` is not available:

```bash
# Push and use the link Git provides
git push -u origin expedition/auth-login-flow
# Git will print a URL to create the PR — use it
```

Or create the PR manually on GitHub using the expedition report template.

### PR Title Convention

```
Expedition: <Journey Name> (<checkpoint-range>)
```

Examples:
- `Expedition: Auth Login Flow (AUTH-01 through AUTH-05)`
- `Fix: Token Expiry Edge Case (AUTH-06)`
- `Expedition: Dashboard Widgets (DASH-01 through DASH-12)`

### PR Body Structure

Use the expedition report template (`.github/PULL_REQUEST_TEMPLATE.md`):

1. **Summary** — One-line description of what trail was cleared
2. **Trail Map** — Final Mermaid diagram with all ✅ markers
3. **Checkpoint Status** — Table with ID, description, status, evidence link
4. **Coverage** — Total, cleared, blocked, percentage
5. **Expedition Log** — Scout phase checklist + Builder phase checklist
6. **Evidence** — Links to `playwright-report/`, `test-results/`, `checkpoints.json`
7. **Test Commands** — How to reproduce locally

### PR Review Checklist (for reviewers)

The PR template should include:

- [ ] All checkpoint tests pass locally (`npm run test:all`)
- [ ] Trail map matches implementation
- [ ] No code outside the expedition scope (YAGNI)
- [ ] Commit history follows Scout → Builder order
- [ ] No secrets, credentials, or `.env` files committed
- [ ] Screenshots/evidence match checkpoint descriptions

## Multi-Agent Branch Strategy

When using Scout and Builder as separate agents:

### Option A: Single Branch (Recommended)

```bash
# Scout creates branch and writes tests
git checkout -b expedition/auth-login-flow
# Scout commits: "Scout: Mark trail for AUTH-01 through AUTH-05"
git push -u origin expedition/auth-login-flow

# Builder pulls the same branch and implements
git checkout expedition/auth-login-flow
git pull origin expedition/auth-login-flow
# Builder commits per checkpoint: "Builder: Clear AUTH-01"
git push origin expedition/auth-login-flow
```

### Option B: Separate Branches (Complex expeditions)

```bash
# Scout works on scout branch
git checkout -b scout/auth-login-flow
# Scout commits tests, pushes, creates PR into expedition branch

# Builder works on builder branch off scout's work
git checkout -b builder/auth-login-flow scout/auth-login-flow
# Builder commits implementation, pushes, creates PR into main
```

Option A is simpler and preferred for most expeditions.

## Common Git Commands for Expeditions

```bash
# Check expedition progress
git log --oneline --graph

# See what changed since branching from main
git log --oneline main..HEAD

# See all files changed in this expedition
git diff --name-only main..HEAD

# Check if branch is up to date with main
git fetch origin main
git log --oneline HEAD..origin/main  # commits on main you don't have

# Rebase on main if needed (before PR)
git fetch origin main
git rebase origin/main

# Squash commits if team prefers (optional)
git rebase -i main  # interactive rebase
```

## Anti-Rationalization

| Rationalization | Counter |
|----------------|---------|
| "I'll just commit to main, it's a small change" | Small changes on main break CI for everyone. Use a branch. |
| "I'll create the PR later" | Later means you'll forget evidence, context, and checkpoint details. Create it now. |
| "Commit messages don't matter" | `git log` is your expedition journal. Future you will thank present you. |
| "I'll push everything in one big commit" | One commit per checkpoint. Smaller = easier to review, bisect, and revert. |
| "I don't need to run tests before committing" | Broken commits waste reviewer time and break CI. Verify first. |
| "The branch name doesn't matter" | Branch names are how teams find, filter, and understand work in progress. Follow the convention. |
