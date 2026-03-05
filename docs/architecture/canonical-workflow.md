# Canonical Workflow Specification

This document is the **single source of truth** for Pathfinder workflow semantics.

## Phases

Pathfinder uses a 5-phase core lifecycle:

1. **Survey** — clarify requirements and constraints.
2. **Plan** — chart the map, define checkpoints, and create task/state files.
3. **Scout** — write failing tests first (RED).
4. **Build** — implement minimal code to pass tests (GREEN).
5. **Report** — verify evidence and produce final delivery artifacts.

## Supported Skills

The canonical skills in this repository are:

- `pathfinder:using-pathfinder`
- `pathfinder:surveying`
- `pathfinder:planning`
- `pathfinder:scouting`
- `pathfinder:unit-testing`
- `pathfinder:building`
- `pathfinder:dispatching`
- `pathfinder:reporting`
- `pathfinder:git-workflow`
- `pathfinder:code-review`
- `pathfinder:security`
- `pathfinder:systematic-debugging`

## Slash Commands

- `/survey` → `pathfinder:surveying`
- `/scout` → `pathfinder:scouting`
- `/build` → `pathfinder:building`
- `/report` → `pathfinder:reporting`

## Gate Files

- Survey produces `.pathfinder/survey.json`
- Plan produces `.pathfinder/plan.json`
- Scout produces `.pathfinder/scout.json`
- Build produces `.pathfinder/build.json`

Each next phase must verify the previous gate exists and is approved/complete.

## Cross-Cutting Skills

These skills apply at any point in the workflow and are not tied to a specific phase:

- `pathfinder:dispatching` — Multi-agent coordination (optional)
- `pathfinder:git-workflow` — Branching, commits, and PRs
- `pathfinder:code-review` — Structured code review
- `pathfinder:security` — Security awareness
- `pathfinder:systematic-debugging` — Root-cause debugging
- `pathfinder:unit-testing` — Unit tests (complements E2E scouting)

## Trail Markers

- ❌ Uncharted
- 🔄 Scouted
- ✅ Cleared
- ⚠️ Unstable
- ⏭️ Skipped
