---
name: using-pathfinder
description: >
  Meta-skill that bootstraps the Pathfinder expedition workflow.
  Automatically loaded at session start via SessionStart hook.
---

# Using Pathfinder

*Marks the trail before others follow.*

## THE RULE

If there is even a 1% chance a Pathfinder skill applies to your current task,
you MUST invoke it. This is not optional. This is not a suggestion.

Thinking "I already know how to do this"? Invoke the skill anyway.
Thinking "It's just a small change"? Invoke the skill anyway.
Thinking "I'll save time by skipping"? You won't. Invoke the skill.

## Skill Routing

| Trigger | Skill | When |
|---------|-------|------|
| New feature, user story, requirement | `pathfinder:surveying` | Before ANY code or tests |
| Need a visual journey/flow | `pathfinder:charting` | After survey approved |
| Defining test cases or checkpoints | `pathfinder:marking` | After map charted |
| Writing E2E or integration tests | `pathfinder:scouting` | After checkpoints marked |
| Writing unit tests for functions/modules | `pathfinder:unit-testing` | Any code in `src/` |
| Implementing features | `pathfinder:building` | After ALL tests written (unit + E2E) |
| Coordinating scout/builder agents | `pathfinder:dispatching` | Multi-agent mode |
| Creating PR or expedition report | `pathfinder:reporting` | After all tests pass |
| Creating branches, committing, opening PRs | `pathfinder:git-workflow` | Start and end of expedition |
| Something is broken/failing | `pathfinder:systematic-debugging` | Any time |
| Claiming task completion | `pathfinder:verification-before-completion` | Before ANY completion claim |

## Process Skills Come First

When multiple skills apply, process skills ALWAYS come before implementation:

1. `pathfinder:surveying` (understand WHAT)
2. `pathfinder:charting` (visualize HOW)
3. `pathfinder:marking` (define checkpoints)
4. `pathfinder:scouting` (write tests)
5. `pathfinder:building` (implement)
6. `pathfinder:reporting` (ship)

"Build X" triggers surveying first. Always.

## Enforcement Gates

- Cannot skip Survey phase for new features
- Cannot write production code without failing tests (both unit AND E2E)
- Cannot mark a checkpoint as cleared without evidence (both test layers must pass)
- Cannot create a PR without all checkpoints passing
- Cannot claim completion without verification

## Trail Markers

| Marker | Name | Meaning |
|--------|------|---------|
| ❌ | Uncharted | Checkpoint identified, no test yet |
| 🔄 | Scouted | Test written, awaiting implementation |
| ✅ | Cleared | Test passing |
| ⚠️ | Unstable | Flaky test needs attention |
| ⏭️ | Skipped | Out of scope for this expedition |

## Anti-Skip Guard

If you find yourself NOT invoking a skill, check these:

| Thought | Reality | Action |
|---------|---------|--------|
| "This is too trivial for the full workflow" | Trivial things break most often | At minimum invoke `pathfinder:scouting` |
| "I already know the requirements" | Assumptions cause rework | Invoke `pathfinder:surveying` |
| "Tests will slow me down" | Tests catch the bugs you'd spend 10x fixing later | Invoke `pathfinder:test-driven-development` |
| "I'll add tests after" | Tests-after are biased by implementation | Delete code, invoke `pathfinder:scouting` |
| "E2E tests are enough, no unit tests needed" | E2E tells you something broke. Unit tests tell you what broke. | Invoke `pathfinder:unit-testing` |
| "I'll commit to main, it's a small change" | Small changes on main break CI for everyone. | Invoke `pathfinder:git-workflow` |
