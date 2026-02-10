---
name: writing-skills
description: >
  Meta-skill for creating new Pathfinder skills using TDD methodology.
  Skills are TDD-tested documentation.
---

# Writing Pathfinder Skills

## Skills Are TDD-Tested Documentation

The same RED-GREEN-REFACTOR cycle applies to skills themselves.

### RED Phase — Observe the Failure

1. Give an agent a task WITHOUT the skill loaded
2. Document what goes wrong:
   - Did it skip the survey?
   - Did it write code before tests?
   - Did it claim completion without evidence?
   - What rationalizations did it use?
3. Record specific failure patterns and rationalizations

### GREEN Phase — Write the Skill

1. Create `skills/<skill-name>/SKILL.md`
2. Address each observed failure explicitly
3. Add anti-rationalization counters for each excuse
4. Add verification requirements for each claim
5. Include concrete examples (code, commands)

### REFACTOR Phase — Close Loopholes

1. Run the scenario again WITH the skill loaded
2. If the agent finds a new way to skip: add a counter
3. If the skill is too verbose: simplify without losing enforcement
4. If agents ignore a section: restructure for scannability

## Skill File Structure

```markdown
---
name: skill-name
description: >
  One-line description of when this skill activates.
---

# Skill Name

**Goal:** What this skill achieves.
**Prerequisite:** What must be true before this skill activates.
**Territory:** What files/directories this skill operates on.

## The Process
[Step-by-step instructions]

## Commands
[Specific CLI commands to run]

## Anti-Rationalization
[Table of rationalizations and counters]
```

## Key Principles

- **Specific over generic** — Address exact failure modes, not abstract advice
- **Commands over prose** — Give copy-pasteable commands, not paragraphs
- **Anti-rationalization is mandatory** — Every skill needs a rationalization table
- **Evidence over claims** — Every verification needs a specific command to run
- **Brevity wins** — Agents have limited context. Every word must earn its place.
