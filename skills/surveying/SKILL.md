---
name: surveying
description: "Explores requirements through collaborative dialogue and creates expedition state with survey gate. Use when starting a new feature or receiving /survey command. Do not use for bug fixes, one-liner changes, or when an expedition is already in progress."
---

# Surveying

## Process

1. **Create feature branch:** `git checkout -b feat/<expedition-name>`
2. **Understand the problem:** Read project files, docs, recent commits. Ask clarifying questions one at a time — use multiple choice where possible.
3. **Propose 2-3 approaches** with trade-offs, effort estimates, and risks. Lead with your recommendation.
4. **Get explicit approval.** Do not proceed without it.

<HARD-GATE>
Do NOT proceed to planning until the user has explicitly approved the design.
</HARD-GATE>

5. **Detect test runners:** Run `python3 scripts/detect-test-runners.py .` — if it fails, ask the user.

6. **Create expedition state:**

```bash
mkdir -p .pathfinder
```

Write `.pathfinder/state.json`:
```json
{
  "version": "0.5.0",
  "expedition": "<name>",
  "branch": "feat/<name>",
  "currentPhase": "survey",
  "testRunners": { "e2e": "<detected>", "unit": "<detected>" },
  "phases": {
    "survey":  { "status": "approved",  "timestamp": "<ISO-8601>" },
    "plan":    { "status": "pending",   "timestamp": null },
    "scout":   { "status": "pending",   "timestamp": null },
    "build":   { "status": "pending",   "timestamp": null },
    "report":  { "status": "pending",   "timestamp": null }
  },
  "checkpoints": { "total": 0, "planned": 0, "red": 0, "green": 0, "verified": 0 }
}
```

Write `.pathfinder/survey.json`:
```json
{
  "status": "approved",
  "timestamp": "<ISO-8601>",
  "expedition": "<name>",
  "designSummary": "<1-2 sentences>",
  "approaches": [{ "name": "...", "selected": true, "reason": "..." }]
}
```

7. **Commit:** `git add .pathfinder/ && git commit -m "Survey: Approve design for <name>"`
8. **Auto-transition** to `pathfinder:planning`.

## Error Handling

- If test runner detection fails, ask the user to confirm frameworks manually.
- If an expedition already exists, ask whether to resume or start fresh.
- If the user hasn't approved after 3 iterations, summarize disagreements and ask for direction.

## Output

- `.pathfinder/state.json` — expedition state
- `.pathfinder/survey.json` — gate file
- Feature branch created
