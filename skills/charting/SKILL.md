---
name: charting
description: >
  Phase 2: Create visual journey diagram with all checkpoints marked.
  Chart the map using Mermaid diagrams in USER-JOURNEYS.md.
---

# Charting — Phase 2

**Goal:** Create visual journey diagram with all checkpoints marked.

**Prerequisite:** Survey approved (Phase 1 complete).

## Create Mermaid Diagram

Create or update `USER-JOURNEYS.md`:

```mermaid
graph TD
    A[Entry Point] --> B{Decision?}
    B -->|Yes| C[Happy Path ❌ FEAT-01]
    B -->|No| D[Alt Path ❌ FEAT-02]
    C --> E[Action ❌ FEAT-03]
    E --> F{Error?}
    F -->|Yes| G[Error State ❌ FEAT-04]
    F -->|No| H[Success ❌ FEAT-05]
```

## Node Format

**Pattern:** `[Description MARKER ID]`

- `[Dashboard ❌ AUTH-01]` — Uncharted checkpoint
- `{Valid Credentials?}` — Decision node (no checkpoint)
- `[Login Page]` — Navigation node (no checkpoint)

## Checkpoint Naming

**Format:** `{JOURNEY}-{NUMBER}`

- `AUTH-01`, `AUTH-02` — Authentication journey
- `DASH-01`, `DASH-02` — Dashboard journey
- `WELL-01`, `WELL-02` — Wells journey

Always uppercase, zero-padded.

## Present in Sections

Don't dump the entire diagram at once. Present in sections:

1. Show the happy path first
2. Add error paths
3. Add edge cases
4. Check after each: "Does this look right so far?"

## YAGNI Check

Before finalizing: "Can any of these checkpoints be removed?"
Every checkpoint is a test that must be written and maintained.
