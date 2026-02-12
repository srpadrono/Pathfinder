# Pathfinder v0.4.0 — Design Document

*Structural enforcement over voluntary discipline.*

## Problem Statement

Agents skip phases. They push to main, skip Report, forget branches. Git hooks (v0.3.0) catch some violations, but the workflow still relies on the agent *choosing* to follow the process. v0.4.0 makes skipping **structurally impossible** by introducing machine-readable task files, dependency enforcement, cross-agent verification, and a quality score.

## What We're Borrowing

| Project | Idea | How We Use It |
|---------|------|---------------|
| claude-bootstrap | Task dependency chains (`addBlockedBy`) | Checkpoints have dependencies; build refuses to work on blocked tasks |
| spec-workflow | Structured task files per feature | `.pathfinder/tasks/FEAT-01.json` per checkpoint |
| claude-code-skills | Quality score (not just pass/fail) | Report phase computes a 0-100 score |
| tdd-guard | Hook reads test results file | Pre-commit reads `state.json` to enforce phase |
| riskjuggler | Post-commit reminder file | `state.json` is always current; hooks + scripts read it |

---

## 1. Architecture Overview

```
.pathfinder/
├── state.json              # Current phase + expedition metadata
├── survey.json             # Survey gate (unchanged from v0.3)
├── plan.json               # Plan gate (extended with task refs)
├── scout.json              # Scout gate (unchanged)
├── build.json              # Build gate (extended)
├── report.json             # NEW: Report gate with quality score
└── tasks/
    ├── FEAT-01.json        # Individual checkpoint task file
    ├── FEAT-02.json
    └── ...
```

**Key change:** Checkpoints move from rows in USER-JOURNEYS.md to individual JSON files with status, dependencies, and evidence. USER-JOURNEYS.md remains as the human-readable trail map (Mermaid diagram + markers), but the **source of truth** is the task files.

---

## 2. File Format Specifications

### 2.1 `state.json` — Expedition State

The single source of truth for "where are we now." Every phase transition updates this. Git hooks and scripts read it.

```json
{
  "version": "0.4.0",
  "expedition": "weather-dashboard",
  "branch": "feat/weather-dashboard",
  "currentPhase": "build",
  "phases": {
    "survey":  { "status": "approved",  "timestamp": "2026-02-11T14:00:00Z" },
    "plan":    { "status": "approved",  "timestamp": "2026-02-11T14:15:00Z" },
    "scout":   { "status": "complete",  "timestamp": "2026-02-11T14:30:00Z" },
    "build":   { "status": "in-progress", "timestamp": "2026-02-11T15:00:00Z" },
    "report":  { "status": "pending",   "timestamp": null }
  },
  "checkpoints": {
    "total": 5,
    "planned": 1,
    "red": 1,
    "green": 2,
    "verified": 1
  }
}
```

**Rules:**
- `currentPhase` can only advance forward: survey → plan → scout → build → report
- `phases[X].status` must be `"approved"` or `"complete"` before `phases[X+1]` can leave `"pending"`
- `branch` must not be `"main"` or `"master"`

### 2.2 Task Files — `.pathfinder/tasks/FEAT-XX.json`

```json
{
  "id": "WDASH-01",
  "description": "Dashboard loads and displays current weather",
  "category": "Happy Path",
  "priority": "must",
  "status": "green",
  "dependencies": [],
  "tests": {
    "e2e": ["e2e/weather-dashboard.spec.ts"],
    "unit": ["src/utils/weather-api.test.ts"]
  },
  "evidence": {
    "red": {
      "e2e": "FAIL e2e/weather-dashboard.spec.ts > WDASH-01 (timeout waiting for locator)",
      "unit": "FAIL src/utils/weather-api.test.ts > WDASH-U01 (expected undefined)",
      "timestamp": "2026-02-11T14:30:00Z"
    },
    "green": {
      "e2e": "PASS e2e/weather-dashboard.spec.ts > WDASH-01 (1.2s)",
      "unit": "PASS src/utils/weather-api.test.ts > WDASH-U01 (3ms)",
      "fullSuite": "Tests: 42 passed, 0 failed",
      "timestamp": "2026-02-11T15:10:00Z"
    },
    "verified": null
  },
  "builderNotes": "Used fetch API with error boundary wrapper"
}
```

**Status lifecycle:** `planned` → `red` → `green` → `verified`

| Status | Meaning | Who sets it |
|--------|---------|-------------|
| `planned` | Checkpoint defined in plan | Planning phase |
| `red` | Tests written and failing | Scout phase |
| `green` | Tests passing after implementation | Build phase |
| `verified` | Independent verification passed | Verify step |

**Dependencies:** Array of checkpoint IDs. Build phase refuses to work on a checkpoint unless all dependencies have status `green` or `verified`.

```json
{
  "id": "WDASH-03",
  "dependencies": ["WDASH-01", "WDASH-02"],
  "status": "red"
}
```

Builder runs: "WDASH-01 is green, WDASH-02 is green → WDASH-03 is unblocked."

### 2.3 `report.json` — Expedition Report (NEW)

```json
{
  "phase": "report",
  "status": "complete",
  "timestamp": "2026-02-11T16:00:00Z",
  "qualityScore": 92,
  "breakdown": {
    "allTestsPass": { "score": 25, "max": 25, "detail": "42 passed, 0 failed" },
    "evidenceComplete": { "score": 20, "max": 20, "detail": "5/5 checkpoints have evidence" },
    "noRegressions": { "score": 20, "max": 20, "detail": "Full suite: 150 passed, 0 failed" },
    "branchHygiene": { "score": 15, "max": 15, "detail": "Branch: feat/weather-dashboard" },
    "prCreated": { "score": 12, "max": 10, "detail": "PR #42 created" },
    "allVerified": { "score": 0, "max": 10, "detail": "3/5 independently verified" }
  },
  "pr": {
    "number": 42,
    "url": "https://github.com/user/repo/pull/42"
  }
}
```

---

## 3. Phase Workflow with Enforcement Points

### 3.1 Survey (unchanged)

Produces: `survey.json`, updates `state.json`

```bash
# At end of survey:
cat > .pathfinder/state.json << 'EOF'
{ "version": "0.4.0", "expedition": "...", "branch": "feat/...",
  "currentPhase": "survey",
  "phases": { "survey": {"status":"approved","timestamp":"..."}, ... } }
EOF
```

### 3.2 Planning (extended)

Produces: `plan.json`, `tasks/FEAT-XX.json` for each checkpoint, updates `state.json`

**New:** Planning creates individual task files with `status: "planned"` and `dependencies`.

```bash
# For each checkpoint:
cat > .pathfinder/tasks/WDASH-01.json << 'EOF'
{"id":"WDASH-01","description":"...","category":"Happy Path",
 "priority":"must","status":"planned","dependencies":[],
 "tests":{"e2e":[],"unit":[]},"evidence":{},"builderNotes":""}
EOF
```

**Dependency assignment:** The planner defines execution order. Happy path checkpoints typically have no dependencies. Error/edge cases depend on the happy path checkpoint they branch from (mirroring the Mermaid diagram edges).

### 3.3 Scouting (extended)

Reads: `plan.json`, task files. Updates each task: `status: "planned"` → `"red"`, fills `tests` and `evidence.red`.

**Enforcement:** Scout reads task files to know what to test. Creates no new checkpoints (only those in plan).

### 3.4 Building (major changes)

**Dependency gate (NEW):** Before working on a checkpoint, builder MUST check:

```bash
# Pseudocode in builder instructions:
for dep in task.dependencies:
  dep_task = read .pathfinder/tasks/${dep}.json
  if dep_task.status not in ["green", "verified"]:
    REFUSE. Print: "Blocked: ${task.id} depends on ${dep} which is ${dep_task.status}"
    exit
```

This is pasted into the builder sub-agent's task text. It's not a hook — it's a structural instruction the agent follows because the task file makes the dependency explicit and checkable.

**After each checkpoint clears:**
1. Update task file: `status: "red"` → `"green"`, fill `evidence.green`
2. Update `state.json` checkpoint counts
3. Commit task file with the implementation

### 3.5 Verification (NEW step, between Build and Report)

After builder marks a checkpoint `green`, a **separate verification step** independently runs the tests.

**Two modes:**

**A. Inline verification (single agent):** The reporting phase re-runs all tests before accepting build results. This already exists in v0.3 but was skippable. Now it's enforced: `verify-expedition.sh` independently runs the test suite and updates task statuses to `verified`.

**B. Cross-agent verification (multi-agent):** Dispatch a separate "verifier" sub-agent that:
1. Reads `.pathfinder/tasks/*.json` where `status == "green"`
2. Runs each checkpoint's tests independently
3. Updates status to `verified` (or back to `red` if they fail)
4. Does NOT trust builder's evidence — captures its own test output

**Verifier dispatch template:**
```
You are a VERIFIER for the Pathfinder expedition.

YOUR JOB: Independently run tests for checkpoints marked "green". 
Do NOT trust the builder's evidence. Run the tests yourself.

For each .pathfinder/tasks/*.json where status is "green":
1. Run: npx playwright test --grep "<checkpoint-id>" --reporter=list
2. Run: npx vitest run --testNamePattern "<checkpoint-id>"
3. If BOTH pass: update status to "verified", fill evidence.verified
4. If EITHER fails: update status back to "red", note the failure

Do NOT modify any source code or test code. Only update task JSON files.
```

### 3.6 Reporting (extended)

**Gate check:** All task files must be `green` or `verified`. Compute quality score. Create PR.

---

## 4. Quality Score Specification

Total: 100 points.

| Criterion | Points | How to check |
|-----------|--------|-------------|
| All checkpoint tests pass | 25 | Run `npm run test:all`, 0 failures |
| Evidence complete | 20 | Every task file has `evidence.green` filled |
| No regressions | 20 | Full suite (not just new tests) passes |
| Branch hygiene | 15 | `state.json.branch` is not main/master |
| PR created | 10 | `gh pr list --head <branch>` returns a PR |
| All verified | 10 | Every task has `status: "verified"` (not just `green`) |

**Thresholds:**
- **90-100:** Excellent expedition. Merge-ready.
- **70-89:** Acceptable. Review carefully.
- **Below 70:** Do not merge. Fix issues first.

---

## 5. Script Specifications

### 5.1 `verify-expedition.sh` (rewritten)

```bash
#!/usr/bin/env bash
# Pathfinder v0.4.0 Expedition Verification
set -euo pipefail

SCORE=0
MAX_SCORE=100
ERRORS=0

echo "🔍 Pathfinder Expedition Verification (v0.4.0)"
echo "================================================"

# --- Check state.json exists ---
if [ ! -f .pathfinder/state.json ]; then
  echo "✘ No .pathfinder/state.json — not a Pathfinder expedition"
  exit 1
fi

BRANCH=$(python3 -c "import json; print(json.load(open('.pathfinder/state.json'))['branch'])")
EXPEDITION=$(python3 -c "import json; print(json.load(open('.pathfinder/state.json'))['expedition'])")
echo "Expedition: $EXPEDITION | Branch: $BRANCH"
echo ""

# --- 1. Gate files (prerequisite, no points) ---
echo "📋 Gate Files"
for gate in survey plan scout build; do
  file=".pathfinder/${gate}.json"
  if [ ! -f "$file" ]; then
    echo "  ✘ Missing: $file"
    ERRORS=$((ERRORS + 1))
  else
    status=$(python3 -c "import json; print(json.load(open('$file')).get('status','?'))")
    if [ "$status" = "approved" ] || [ "$status" = "complete" ]; then
      echo "  ✓ $file ($status)"
    else
      echo "  ✘ $file: status=$status (expected approved/complete)"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done
echo ""

if [ "$ERRORS" -gt 0 ]; then
  echo "✘ Gate files incomplete. Cannot compute quality score."
  exit 1
fi

# --- 2. Task files: evidence check (20 pts) ---
echo "📋 Task Evidence"
TASK_COUNT=0
EVIDENCE_COUNT=0
VERIFIED_COUNT=0
for task_file in .pathfinder/tasks/*.json; do
  [ -f "$task_file" ] || continue
  TASK_COUNT=$((TASK_COUNT + 1))
  id=$(python3 -c "import json; print(json.load(open('$task_file'))['id'])")
  status=$(python3 -c "import json; print(json.load(open('$task_file'))['status'])")
  has_evidence=$(python3 -c "
import json
t = json.load(open('$task_file'))
print('yes' if t.get('evidence',{}).get('green') else 'no')
")
  if [ "$has_evidence" = "yes" ]; then
    EVIDENCE_COUNT=$((EVIDENCE_COUNT + 1))
    echo "  ✓ $id ($status) — evidence present"
  else
    echo "  ⚠ $id ($status) — NO evidence"
  fi
  if [ "$status" = "verified" ]; then
    VERIFIED_COUNT=$((VERIFIED_COUNT + 1))
  fi
done

if [ "$TASK_COUNT" -gt 0 ]; then
  EVIDENCE_SCORE=$((20 * EVIDENCE_COUNT / TASK_COUNT))
  VERIFIED_SCORE=$((10 * VERIFIED_COUNT / TASK_COUNT))
else
  EVIDENCE_SCORE=0
  VERIFIED_SCORE=0
fi
SCORE=$((SCORE + EVIDENCE_SCORE + VERIFIED_SCORE))
echo "  Evidence: $EVIDENCE_COUNT/$TASK_COUNT ($EVIDENCE_SCORE/20 pts)"
echo "  Verified: $VERIFIED_COUNT/$TASK_COUNT ($VERIFIED_SCORE/10 pts)"
echo ""

# --- 3. Run tests (25 pts for checkpoint tests, 20 pts for no regressions) ---
echo "📋 Test Suite"
if npm run test:all > /tmp/pathfinder-test-output.txt 2>&1; then
  echo "  ✓ All tests pass"
  SCORE=$((SCORE + 25 + 20))
  TESTS_DETAIL=$(tail -5 /tmp/pathfinder-test-output.txt)
else
  echo "  ✘ Tests failed"
  TESTS_DETAIL=$(tail -10 /tmp/pathfinder-test-output.txt)
  # Partial: if only new tests fail but old pass, give regression points
  # For simplicity, 0 for both if anything fails
fi
echo "$TESTS_DETAIL" | sed 's/^/  /'
echo ""

# --- 4. Branch hygiene (15 pts) ---
echo "📋 Branch Hygiene"
if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "master" ]; then
  echo "  ✓ On feature branch: $BRANCH"
  SCORE=$((SCORE + 15))
else
  echo "  ✘ On $BRANCH — must use feature branch"
fi
echo ""

# --- 5. PR created (10 pts) ---
echo "📋 Pull Request"
PR_URL=$(gh pr list --head "$BRANCH" --json url --jq '.[0].url' 2>/dev/null || echo "")
if [ -n "$PR_URL" ]; then
  echo "  ✓ PR exists: $PR_URL"
  SCORE=$((SCORE + 10))
else
  echo "  ⚠ No PR found for branch $BRANCH"
fi
echo ""

# --- 6. Security check ---
echo "📋 Security"
secrets=$(git diff --name-only main..HEAD 2>/dev/null | grep -E '\.env$|\.env\.local|secrets|credentials' || true)
if [ -n "$secrets" ]; then
  echo "  ✘ Potential secrets in diff: $secrets"
else
  echo "  ✓ No secret files in diff"
fi
echo ""

# --- Summary ---
echo "================================================"
echo "Quality Score: $SCORE / $MAX_SCORE"
if [ "$SCORE" -ge 90 ]; then
  echo "🟢 Excellent — merge-ready"
elif [ "$SCORE" -ge 70 ]; then
  echo "🟡 Acceptable — review carefully"
else
  echo "🔴 Below threshold — fix issues before merge"
fi

# --- Write report.json ---
cat > .pathfinder/report.json << EOF
{
  "phase": "report",
  "status": "complete",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "qualityScore": $SCORE,
  "breakdown": {
    "allTestsPass": {"score": $((SCORE >= 60 ? 25 : 0)), "max": 25},
    "evidenceComplete": {"score": $EVIDENCE_SCORE, "max": 20},
    "noRegressions": {"score": $((SCORE >= 60 ? 20 : 0)), "max": 20},
    "branchHygiene": {"score": $((BRANCH != "main" && BRANCH != "master" ? 15 : 0)), "max": 15},
    "prCreated": {"score": $((PR_URL ? 10 : 0)), "max": 10},
    "allVerified": {"score": $VERIFIED_SCORE, "max": 10}
  },
  "pr": {"url": "${PR_URL:-null}"}
}
EOF
echo ""
echo "Report saved to .pathfinder/report.json"

exit $((SCORE < 70 ? 1 : 0))
```

### 5.2 `pathfinder-check-deps.sh` (NEW helper)

Called by builder before working on a checkpoint:

```bash
#!/usr/bin/env bash
# Usage: pathfinder-check-deps.sh WDASH-03
set -euo pipefail
TASK_ID=$1
TASK_FILE=".pathfinder/tasks/${TASK_ID}.json"

if [ ! -f "$TASK_FILE" ]; then
  echo "✘ Task file not found: $TASK_FILE"
  exit 1
fi

BLOCKED=0
python3 -c "
import json, sys
task = json.load(open('$TASK_FILE'))
for dep in task.get('dependencies', []):
    dep_file = f'.pathfinder/tasks/{dep}.json'
    try:
        dep_task = json.load(open(dep_file))
        if dep_task['status'] not in ('green', 'verified'):
            print(f'✘ Blocked: {task[\"id\"]} depends on {dep} (status: {dep_task[\"status\"]})')
            sys.exit(1)
    except FileNotFoundError:
        print(f'✘ Dependency task file missing: {dep_file}')
        sys.exit(1)
print(f'✓ {task[\"id\"]} is unblocked — all dependencies satisfied')
"
```

### 5.3 `pathfinder-update-state.sh` (NEW helper)

Updates `state.json` checkpoint counts from task files:

```bash
#!/usr/bin/env bash
set -euo pipefail
python3 -c "
import json, glob
state = json.load(open('.pathfinder/state.json'))
counts = {'total':0,'planned':0,'red':0,'green':0,'verified':0}
for f in sorted(glob.glob('.pathfinder/tasks/*.json')):
    t = json.load(open(f))
    counts['total'] += 1
    counts[t['status']] = counts.get(t['status'], 0) + 1
state['checkpoints'] = counts
json.dump(state, open('.pathfinder/state.json','w'), indent=2)
print(f'State updated: {counts}')
"
```

---

## 6. Git Hook Specifications

### 6.1 `pre-commit` (updated)

```bash
#!/usr/bin/env bash
# Pathfinder v0.4.0 pre-commit hook

# Skip if not a pathfinder expedition
[ -f .pathfinder/state.json ] || exit 0

STATE_FILE=".pathfinder/state.json"
PHASE=$(python3 -c "import json; print(json.load(open('$STATE_FILE'))['currentPhase'])")

# Get staged files
STAGED=$(git diff --cached --name-only)

# Rule 1: No source code changes during survey/plan/scout phases
if echo "$PHASE" | grep -qE "^(survey|plan|scout)$"; then
  SRC_CHANGES=$(echo "$STAGED" | grep -E "^src/" | grep -v "\.test\." || true)
  if [ -n "$SRC_CHANGES" ]; then
    echo "✘ Pathfinder: Cannot modify source code during $PHASE phase."
    echo "  Blocked files: $SRC_CHANGES"
    echo "  Current phase: $PHASE — only test files allowed."
    exit 1
  fi
fi

# Rule 2: No test modifications during build phase (unless switching to scout)
# (Advisory — hard to enforce perfectly, but catches obvious violations)

# Rule 3: Build gate requires scout gate
if echo "$STAGED" | grep -q ".pathfinder/build.json"; then
  if [ ! -f .pathfinder/scout.json ]; then
    echo "✘ Pathfinder: Cannot create build gate without scout gate."
    exit 1
  fi
fi

# Rule 4: Report gate requires build gate
if echo "$STAGED" | grep -q ".pathfinder/report.json"; then
  if [ ! -f .pathfinder/build.json ]; then
    echo "✘ Pathfinder: Cannot create report gate without build gate."
    exit 1
  fi
fi

exit 0
```

### 6.2 `pre-push` (unchanged from v0.3)

Blocks push to main/master. Forces feature branches.

### 6.3 `post-commit` (NEW — inspired by riskjuggler)

After every commit, refresh `state.json` so the agent always has current context:

```bash
#!/usr/bin/env bash
# Pathfinder post-commit: update state after every commit
[ -f .pathfinder/state.json ] || exit 0
bash scripts/pathfinder-update-state.sh 2>/dev/null || true
```

---

## 7. Updated Phase Instructions for Sub-Agents

Since sub-agents get task text pasted (not file access to skill repo), the key changes to dispatch templates:

### Builder Dispatch (v0.4.0)

Add to the existing builder template:

```
=== DEPENDENCY CHECK (before each checkpoint) ===

Before working on any checkpoint, run:
  bash scripts/pathfinder-check-deps.sh <CHECKPOINT-ID>

If it says "Blocked" → skip this checkpoint and move to the next unblocked one.
Report which checkpoints were blocked and why.

=== TASK FILE UPDATES (after each checkpoint) ===

After clearing a checkpoint, update its task file:
  python3 -c "
  import json
  t = json.load(open('.pathfinder/tasks/<ID>.json'))
  t['status'] = 'green'
  t['evidence']['green'] = {
    'e2e': '<paste e2e pass output>',
    'unit': '<paste unit pass output>',
    'fullSuite': '<paste full suite summary>',
    'timestamp': '<ISO timestamp>'
  }
  json.dump(t, open('.pathfinder/tasks/<ID>.json','w'), indent=2)
  "
  git add .pathfinder/tasks/<ID>.json
```

---

## 8. Migration from v0.3.x

### What changes:
1. **New file:** `.pathfinder/state.json` — created at expedition start
2. **New directory:** `.pathfinder/tasks/` — created during Planning
3. **New file:** `.pathfinder/report.json` — created by verify-expedition.sh
4. **Updated:** `verify-expedition.sh` — rewritten with quality score
5. **New scripts:** `pathfinder-check-deps.sh`, `pathfinder-update-state.sh`
6. **Updated hooks:** `pre-commit` reads `state.json`, new `post-commit`
7. **New phase:** Verification (between Build and Report)

### What doesn't change:
- Expedition metaphor and phase names
- Gate file concept (survey.json, plan.json, scout.json, build.json)
- USER-JOURNEYS.md with Mermaid diagrams and trail markers
- Evidence block format in markdown
- Dispatch template structure
- Anti-rationalization tables

### Migration steps:
1. Update `scripts/verify-expedition.sh` with new version
2. Add `scripts/pathfinder-check-deps.sh` and `scripts/pathfinder-update-state.sh`
3. Update `.githooks/pre-commit` 
4. Add `.githooks/post-commit`
5. Update skill SKILL.md files to reference task files and state.json
6. Existing in-progress expeditions: create state.json and task files from existing gate files (one-time backfill)

---

## 9. Design Principles

1. **Enforcement in the structure, not the instructions.** Task files with dependencies make invalid states unrepresentable. The builder literally cannot find an unblocked task if dependencies aren't met.

2. **Machine-readable over human-readable.** JSON task files can be parsed by hooks and scripts. Markdown evidence blocks are kept for human review but aren't the enforcement mechanism.

3. **Don't trust the builder.** Independent verification step re-runs tests. Quality score penalizes unverified checkpoints.

4. **Complexity in enforcement, simplicity in usage.** The agent experience is: "read task file → check deps → build → update task file → commit." The hooks and scripts handle the rest.

5. **Graceful degradation.** If scripts aren't available (e.g., sub-agent can't run bash), the JSON task files still communicate dependencies via their structure. The agent reads the dependency array and checks sibling task files manually.
