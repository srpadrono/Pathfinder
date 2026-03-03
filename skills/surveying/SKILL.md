---
name: surveying
description: "Explores requirements through collaborative dialogue and creates expedition state with survey gate. Use when starting a new feature or receiving /survey command. Do not use for bug fixes, one-liner changes, or when an expedition is already in progress."
---

# Surveying

*Understand the terrain before marking the trail.*

## Overview

Surveying wraps `superpowers:brainstorming` with expedition state management. You explore the problem space, refine requirements, and get design approval — then Pathfinder records the result as a gate file.

**Announce at start:** "I'm using the pathfinder:surveying skill to explore this feature."

## Prerequisites

- Must be on a feature branch (or will create one)
- No existing expedition in progress (or explicitly starting a new one)

## The Process

### Step 1: Create Feature Branch

If not already on a feature branch:

```bash
git checkout -b feat/<expedition-name>
```

### Step 2: Invoke Brainstorming

Follow `superpowers:brainstorming` completely:
1. Understand project context (read files, docs, recent commits)
2. Ask clarifying questions ONE AT A TIME (use multiple choice where possible)
3. Focus on: purpose, constraints, success criteria, edge cases, error states
4. Present design in digestible chunks
5. Get explicit user approval

<HARD-GATE>
Do NOT proceed to planning until the user has explicitly approved the design.
</HARD-GATE>

### Step 3: Propose Approaches

After surveying, propose 2-3 approaches with trade-offs:
- Lead with your recommendation
- Include effort estimates
- Note risks and dependencies
- Get sign-off before continuing

### Step 4: Detect Test Runners

Execute: `python3 scripts/detect-test-runners.py .` to auto-detect frameworks.

Before creating state, detect the project's test frameworks:

| File found | Set e2e to | Set unit to |
|------------|-----------|-------------|
| `playwright.config.ts` | `playwright` | — |
| `e2e/.maestro/config.yaml` | `maestro` | — |
| `cypress.config.ts` | `cypress` | — |
| `.detoxrc.js` | `detox` | — |
| `vitest.config.ts` | — | `vitest` |
| `jest.config.*` | — | `jest` |
| `pytest.ini` / `pyproject.toml` | — | `pytest` |
| `go.mod` | — | `gotest` |
| `Package.swift` | — | `xctest` |

If nothing detected, ask the user. Default: `playwright` + `vitest`.

### Step 5: Create Expedition State

After design approval, create the expedition state:

```bash
mkdir -p .pathfinder

cat > .pathfinder/state.json << 'EOF'
{
  "version": "0.4.0",
  "expedition": "<expedition-name>",
  "branch": "feat/<expedition-name>",
  "currentPhase": "survey",
  "testRunners": {
    "e2e": "<detected-e2e-runner>",
    "unit": "<detected-unit-runner>"
  },
  "phases": {
    "survey":  { "status": "approved",  "timestamp": "<ISO-8601>" },
    "plan":    { "status": "pending",   "timestamp": null },
    "scout":   { "status": "pending",   "timestamp": null },
    "build":   { "status": "pending",   "timestamp": null },
    "report":  { "status": "pending",   "timestamp": null }
  },
  "checkpoints": {
    "total": 0,
    "planned": 0,
    "red": 0,
    "green": 0,
    "verified": 0
  }
}
EOF
```

### Step 6: Create Survey Gate

```bash
cat > .pathfinder/survey.json << 'EOF'
{
  "status": "approved",
  "timestamp": "<ISO-8601>",
  "expedition": "<expedition-name>",
  "designSummary": "<1-2 sentence summary of approved design>",
  "approaches": [
    {
      "name": "<approach name>",
      "selected": true/false,
      "reason": "<why selected or rejected>"
    }
  ]
}
EOF
```

### Step 7: Commit

```bash
git add .pathfinder/state.json .pathfinder/survey.json
git commit -m "Survey: Approve design for <expedition-name>"
```

### Step 8: Transition to Planning

Announce: "Survey complete. Ready for planning — invoke `pathfinder:planning` or say `/scout` to continue."

Automatically invoke `pathfinder:planning` to break the approved design into tasks.

## Error Handling
* If test runner detection fails, run `python3 scripts/detect-test-runners.py .` and ask the user to confirm frameworks.
* If the user hasn't approved the design after 3 iterations, summarize remaining disagreements and ask for explicit direction.
* If an expedition already exists (`.pathfinder/state.json` present), ask whether to resume or start fresh.

## Output

- `.pathfinder/state.json` — expedition state with survey phase approved
- `.pathfinder/survey.json` — gate file with design summary
- Feature branch created (if needed)
