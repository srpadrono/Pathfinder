---
name: using-pathfinder
description: >
  Meta-skill that bootstraps the Pathfinder expedition workflow.
  Automatically loaded at session start via SessionStart hook.
---

# Using Pathfinder

*Marks the trail before others follow.*

## When to Use Pathfinder Skills

Pathfinder skills exist because undisciplined development produces buggy, untested code.
When you're about to write code, check if a Pathfinder skill applies. The cost of
checking is low; the cost of skipping is high (rework, bugs, missing tests).

If you're unsure whether to invoke a skill, invoke it. It's cheaper to read a skill
and decide it doesn't apply than to skip it and realize later you needed it.

## Skill Routing

| Trigger | Skill | When |
|---------|-------|------|
| New feature, user story, requirement | `pathfinder:surveying` | Before ANY code or tests |
| Charting journey map, defining checkpoints | `pathfinder:planning` | After survey approved |
| Writing E2E or integration tests | `pathfinder:scouting` | After plan approved |
| Writing unit tests for functions/modules | `pathfinder:unit-testing` | Any code in `src/` |
| Implementing features | `pathfinder:building` | After ALL tests written (unit + E2E) |
| Coordinating scout/builder agents | `pathfinder:dispatching` | Multi-agent mode |
| Creating PR or expedition report | `pathfinder:reporting` | After all tests pass |
| Creating branches, committing, opening PRs | `pathfinder:git-workflow` | Start and end of expedition |
| Reviewing code or PRs | `pathfinder:code-review` | Any review task |
| Security concern or writing auth/input code | `pathfinder:security` | Any time |
| Something is broken/failing | `pathfinder:systematic-debugging` | Any time |

## Process Order

1. `pathfinder:surveying` (understand WHAT)
2. `pathfinder:planning` (chart map + define checkpoints)
3. `pathfinder:scouting` (write failing tests — E2E + unit)
4. `pathfinder:building` (implement to pass tests)
5. `pathfinder:reporting` (verify evidence + create PR)

"Build X" triggers surveying first. Always.

## Enforcement Gates

- Cannot skip Survey phase for new features
- Cannot write production code without failing tests (both unit AND E2E)
- Cannot mark a checkpoint as cleared without evidence (both test layers must pass)
- Cannot create a PR without all checkpoints passing
- Cannot claim completion without running `npm run test:all`

### Gate Files (Machine-Enforceable)

Each phase produces a gate file that the next phase MUST verify exists before proceeding.
Gate files live in `.pathfinder/` at the project root.

| Phase | Produces | Next Phase Checks |
|-------|----------|-------------------|
| Survey | `.pathfinder/survey.json` | Planning reads it or STOPS |
| Planning | `.pathfinder/plan.json` + `USER-JOURNEYS.md` | Scouting reads it or STOPS |
| Scouting | `.pathfinder/scout.json` | Building reads it or STOPS |
| Building | `.pathfinder/build.json` | Reporting reads it or STOPS |

**Gate file format:**
```json
{
  "phase": "survey",
  "status": "approved",
  "timestamp": "2026-02-11T14:00:00Z",
  "approvedBy": "user"
}
```

**Hard rule:** If the gate file for the previous phase does not exist or has `"status": "pending"`,
the current phase MUST refuse to proceed. No exceptions. No "I'll create it retroactively."

## Trail Markers

| Marker | Name | Meaning |
|--------|------|---------|
| ❌ | Uncharted | Checkpoint identified, no test yet |
| 🔄 | Scouted | Test written, awaiting implementation |
| ✅ | Cleared | Test passing |
| ⚠️ | Unstable | Flaky test needs attention |
| ⏭️ | Skipped | Out of scope for this expedition |

## Anti-Skip Guard

| Thought | Reality | Action |
|---------|---------|--------|
| "This is too trivial for the full workflow" | Trivial things break most often | At minimum invoke `pathfinder:scouting` |
| "I already know the requirements" | Assumptions cause rework | Invoke `pathfinder:surveying` |
| "Tests will slow me down" | Tests catch bugs you'd spend 10x fixing later | Invoke `pathfinder:scouting` |
| "I'll add tests after" | Tests-after are biased by implementation | Delete code, invoke `pathfinder:scouting` |
| "E2E tests are enough" | E2E tells you something broke. Unit tests tell you what. | Invoke `pathfinder:unit-testing` |
| "I'll commit to main" | Small changes on main break CI for everyone. | Invoke `pathfinder:git-workflow` |
| "Security doesn't apply here" | Every user input is an attack vector. | Invoke `pathfinder:security` |

When in doubt, the cost of invoking a skill you don't need is a few seconds of reading.
The cost of skipping a skill you did need is rework, bugs, and missing test coverage.

## Tool Mapping

Skills reference tools by their canonical names. Map to your platform:

| Canonical Tool | Claude Code | Codex |
|----------------|-------------|-------|
| Load a skill | `Skill` tool | Read `skills/` file |
| Read file | `Read` | `read_file` |
| Edit file | `Edit` | `edit_file` |
| Run command | `Bash` | `shell` |

When a skill references a tool by name, use your platform's equivalent from this table.
