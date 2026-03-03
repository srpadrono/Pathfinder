---
name: reporting
description: "Independently verifies all tests, computes quality score, and creates a PR with expedition report. Use after all checkpoints are green and building is complete. Do not use before build phase completes or for informal progress updates."
---

# Reporting

*Verify the trail before declaring it open.*

## Overview

Reporting wraps `superpowers:verification-before-completion` and `superpowers:finishing-a-development-branch`. You independently re-run all tests, verify checkpoints, compute a quality score, and create a PR.

**Announce at start:** "I'm using the pathfinder:reporting skill to verify and finalize this expedition."

## Prerequisites

- `.pathfinder/state.json` exists with `phases.build.status === "complete"`
- All task files have `status: "green"`
- Build gate exists: `.pathfinder/build.json`

<HARD-GATE>
If build is not complete, REFUSE to report. Invoke pathfinder:building first.
No completion claims without fresh verification evidence.
</HARD-GATE>

## The Process

### Step 1: Independent Verification

Do NOT trust builder evidence. Re-run everything fresh using the configured test runners from `state.json`. See `docs/test-runners.md` for commands.

```bash
# Run full test suite (use configured runners)
# e.g. npx playwright test, maestro test, pytest, etc.
<e2e runner command> 2>&1 | tee /tmp/pathfinder-verify.txt
<unit runner command> 2>&1 | tee -a /tmp/pathfinder-verify.txt
```

### Step 2: Verify Each Checkpoint

For each task file with `status: "green"`, run its tests individually using the configured runners.

If tests pass, update task to `verified`:

```python
import json, datetime
task = json.load(open('.pathfinder/tasks/FEAT-01.json'))
task['status'] = 'verified'
task['evidence']['verified'] = {
    'output': '<paste actual test output>',
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}
json.dump(task, open('.pathfinder/tasks/FEAT-01.json', 'w'), indent=2)
```

If tests FAIL, update back to `red` and report the failure.

### Step 3: Run Quality Score

```bash
bash scripts/verify-expedition.sh
```

This computes a 0-100 quality score:

| Criterion | Points | Check |
|-----------|--------|-------|
| All checkpoint tests pass | 25 | Run test suite, 0 failures |
| Evidence complete | 15 | Every task has `evidence.green` filled |
| No regressions | 20 | Full suite passes (not just new tests) |
| Branch hygiene | 10 | On feature branch, not main/master |
| PR created | 10 | PR exists for this branch |
| All verified | 10 | Every task has `status: "verified"` |
| Documentation complete | 10 | PR has dependency graph + user journey map |

**Thresholds:**
- 🟢 **90-100:** Excellent — merge-ready
- 🟡 **70-89:** Acceptable — review carefully
- 🔴 **Below 70:** Do not merge — fix issues first

### Step 3b: Compute Quality Score

Execute: `python3 scripts/compute-quality-score.py .pathfinder/tasks` to generate the quality report.

### Step 4: Create Report Gate

The `verify-expedition.sh` script creates `.pathfinder/report.json` automatically. If running manually:

```python
import json, datetime
report = {
    'phase': 'report',
    'status': 'complete',
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
    'qualityScore': <score>,
    'breakdown': {
        'allTestsPass': {'score': <n>, 'max': 25},
        'evidenceComplete': {'score': <n>, 'max': 20},
        'noRegressions': {'score': <n>, 'max': 20},
        'branchHygiene': {'score': <n>, 'max': 15},
        'prCreated': {'score': <n>, 'max': 10},
        'allVerified': {'score': <n>, 'max': 10}
    },
    'pr': {'number': <n>, 'url': '<url>'}
}
json.dump(report, open('.pathfinder/report.json', 'w'), indent=2)
```

### Step 5: Create PR

Follow `superpowers:finishing-a-development-branch`.

<HARD-GATE>
The PR body MUST include:
1. Mermaid dependency graph showing all checkpoints with status
2. User journey map (Mermaid journey diagram)
3. Checkpoint table with test counts
4. Quality score breakdown
5. Test results

Missing any of these = documentation incomplete = -10 points on quality score.
</HARD-GATE>

```bash
git add .pathfinder/
git commit -m "Report: Expedition <name> complete (score: <N>/100)"

gh pr create \
  --title "feat: <expedition-name>" \
  --body "## Pathfinder Expedition Report

**Expedition:** <name>
**Quality Score:** <score>/100

### Dependency Graph

\`\`\`mermaid
graph TD
    FEAT-01[\"✅ FEAT-01: Description\"] --> FEAT-03[\"✅ FEAT-03: Description\"]
    FEAT-02[\"✅ FEAT-02: Description\"] --> FEAT-03
    style FEAT-01 fill:#22c55e,color:#fff
    style FEAT-02 fill:#22c55e,color:#fff
    style FEAT-03 fill:#22c55e,color:#fff
\`\`\`

### User Journey Map

\`\`\`mermaid
journey
    title <Feature Name>
    section <First Flow>
      Step one: 5: User
      Step two: 5: App
    section <Second Flow>
      Step three: 5: User
\`\`\`

### Checkpoints
| ID | Description | Tests | Status |
|----|-------------|-------|--------|
| FEAT-01 | ... | N unit | ✅ verified |
| FEAT-02 | ... | N unit, N e2e | ✅ verified |

### Quality Breakdown
| Criterion | Score |
|-----------|-------|
| All tests pass | <n>/25 |
| Evidence complete | <n>/15 |
| No regressions | <n>/20 |
| Branch hygiene | <n>/10 |
| PR created | <n>/10 |
| All verified | <n>/10 |
| Documentation complete | <n>/10 |
| **Total** | **<n>/100** |

### Test Results
\`\`\`
<paste full suite output>
\`\`\`
"
```

### Step 6: Update State

```python
import json
state = json.load(open('.pathfinder/state.json'))
state['currentPhase'] = 'report'
state['phases']['report'] = {'status': 'complete', 'timestamp': '<ISO-8601>'}
json.dump(state, open('.pathfinder/state.json', 'w'), indent=2)
```

### Step 7: Announce Completion

Present the quality score and PR link. If score is below 70, list what needs fixing.

## Cross-Agent Verification (Optional)

For higher confidence, dispatch a separate verifier subagent:

```
You are a VERIFIER for the Pathfinder expedition.

YOUR JOB: Independently run tests for checkpoints marked "green".
Do NOT trust the builder's evidence. Run the tests yourself.

For each .pathfinder/tasks/*.json where status is "green":
1. Run e2e tests for this checkpoint (using configured runner from state.json)
2. Run unit tests for this checkpoint (using configured runner from state.json)
3. See docs/test-runners.md for the exact commands per framework
4. If BOTH pass: update status to "verified", fill evidence.verified
5. If EITHER fails: update status back to "red", note the failure

Do NOT modify any source code or test code. Only update task JSON files.
```

## Error Handling
* If `scripts/compute-quality-score.py` returns a score below 70, list failing criteria and fix before creating the PR.
* If a previously-green checkpoint fails during verification, update its status back to `red` and report the regression.
* If `gh pr create` fails, verify the branch has been pushed and the GitHub CLI is authenticated (`gh auth status`).

## Output

- `.pathfinder/report.json` — quality score and breakdown
- `.pathfinder/tasks/FEAT-XX.json` — all updated to `status: "verified"`
- Updated `.pathfinder/state.json` — report phase complete
- Pull request created with expedition report
