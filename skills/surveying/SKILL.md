---
name: surveying
description: >
  Phase 1: Understand requirements through Socratic dialogue before any code.
  Survey the terrain, identify hazards, propose approaches.
---

# Surveying — Phase 1

**Goal:** Understand requirements through Socratic dialogue before any implementation.

## The Process

1. **Check project context first** — Read files, docs, recent commits
2. **Ask questions ONE AT A TIME** — Don't overwhelm
3. **Prefer multiple choice** — Easier to answer than open-ended
4. **Focus on:** Purpose, constraints, success criteria, edge cases

## Example Questions

- "What happens if no data exists? (a) Show empty state (b) Redirect (c) Other"
- "Should state persist on refresh?"
- "How should API errors display? (a) Toast (b) Inline (c) Modal"
- "What's the expected behavior for invalid input?"

## Identify Hazards

Every journey has hazards. Survey for ALL of these:

- Error states (API failures, network errors, timeouts)
- Empty states (no data, first-time user)
- Loading states (slow connections, large datasets)
- Edge cases (boundary values, special characters)
- Race conditions (concurrent updates, stale data)
- Authentication/authorization (expired tokens, insufficient permissions)

## After Surveying

1. Propose 2-3 approaches with trade-offs
2. Lead with your recommendation and reasoning
3. Get sign-off before charting
4. Present in sections (200-300 words each)
5. Check after each section: "Does this look right so far?"

## Gate File

After user approves the survey, create `.pathfinder/survey.json`:

```bash
mkdir -p .pathfinder
cat > .pathfinder/survey.json << 'EOF'
{
  "phase": "survey",
  "status": "approved",
  "timestamp": "<ISO-8601>",
  "summary": "<one-line summary of what was surveyed>",
  "approach": "<chosen approach>",
  "approvedBy": "user"
}
EOF
git add .pathfinder/survey.json
git commit -m "Survey: Approved — <summary>"
```

**The Planning phase will refuse to proceed without this file.**

## YAGNI Check

Before finalizing survey results, ask: "Can any of these requirements be removed?"
Strip everything that isn't essential for the current expedition.

## Anti-Rationalization

| Rationalization | Counter |
|----------------|---------|
| "The requirements are obvious" | Obvious requirements have hidden edge cases. Survey anyway. |
| "I'll figure it out as I go" | Figuring-it-out-as-you-go produces 3x the rework. |
| "The user didn't ask for a survey" | They asked for working software. Survey produces that. |
