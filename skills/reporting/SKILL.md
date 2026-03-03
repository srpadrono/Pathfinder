---
name: reporting
description: "Independently verifies all tests, computes quality score, and creates a PR with expedition report. Use after all checkpoints are green and building is complete. Do not use before build phase completes or for informal progress updates."
---

# Reporting

<HARD-GATE>
Requires `phases.build.status === "complete"`. No completion claims without fresh verification evidence.
PR body MUST include: Mermaid dependency graph, user journey map, checkpoint table, quality score breakdown, test results.
</HARD-GATE>

## Process

1. **Re-run the full test suite.** Do NOT trust builder evidence.
2. **Verify each checkpoint individually.** For each green task, run its tests. If they pass → update to `verified`. If they fail → update back to `red`.
3. **Compute quality score:** `python3 scripts/compute-quality-score.py .pathfinder/tasks`
4. **Create report gate** (`.pathfinder/report.json`) — the script outputs this.
5. **Push and create PR:**

```bash
git push origin <branch>
gh pr create --title "feat: <expedition-name>" --body "<report>"
```

PR body template:
```
## Pathfinder Expedition Report
**Quality Score:** <N>/100

### Dependency Graph
(Mermaid graph with ✅ status on each node)

### User Journey Map
(Mermaid journey diagram)

### Checkpoints
| ID | Description | Tests | Status |
|----|-------------|-------|--------|

### Quality Breakdown
| Criterion | Score |
|-----------|-------|

### Test Results
(paste full suite output)
```

6. **Update state:** `currentPhase: "report"`, `phases.report.status: "complete"`.
7. **Commit:** `git add .pathfinder/ && git commit -m "Report: <name> complete (score: N/100)"`

## Error Handling

- Score below 70 → list failing criteria and fix before creating the PR.
- Previously-green checkpoint fails → update to `red`, report the regression.
- `gh pr create` fails → verify branch is pushed, `gh auth status` is OK.

## Output

- `.pathfinder/report.json` — quality score and breakdown
- All tasks updated to `status: "verified"`
- Pull request with full expedition report
