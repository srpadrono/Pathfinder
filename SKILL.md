---
name: pathfinder
description: >
  TDD workflow using expedition metaphor: scouts write tests, builders implement.
  Maps user journeys with Mermaid diagrams and trail markers (❌→🔄→✅).
  Composable skills architecture with Playwright CLI integration.
tags:
  - tdd
  - testing
  - playwright
  - e2e
  - workflow
  - ai-agent
author: srpadrono
repository: https://github.com/srpadrono/Pathfinder
license: MIT
version: 0.4.0
---

# Pathfinder

*Marks the trail before others follow.*

A TDD workflow skill for AI coding agents using an expedition metaphor.
Scouts survey and write tests, Builders implement until all tests pass.

## Quick Start

0. **Create a feature branch FIRST**: `git checkout -b feat/expedition-name`
1. Read `AGENTS.md` for the full workflow
2. Use `/survey` to start a new feature
3. Use `/scout` to write tests
4. Use `/build` to implement
5. Use `/report` to run verification + create PR
6. **Merge via PR only** — never push directly to main

## Enforcement

Git hooks in `.githooks/` physically block violations:
- **pre-push**: Blocks direct push to main/master
- **pre-commit**: Reads `state.json`, enforces phase ordering (no src/ changes during scout, scout before build)
- **post-commit**: Auto-updates `state.json` checkpoint counts from task files
- **GitHub branch protection**: Server-side backup (set up by repo owner)

Install hooks: `git config core.hooksPath .githooks`

## Task-Level Tracking (v0.4.0)

Checkpoints are individual JSON files in `.pathfinder/tasks/`:
- **state.json** — Current phase + expedition metadata (single source of truth)
- **tasks/FEAT-XX.json** — Per-checkpoint status, dependencies, and evidence
- **Status lifecycle:** `planned` → `red` → `green` → `verified`
- **Dependency enforcement:** Builder refuses blocked checkpoints
- **Quality score:** 0-100 computed by `verify-expedition.sh`

## Skills

Individual skills in `skills/` provide focused instructions per phase.
SessionStart hook auto-loads `skills/using-pathfinder/SKILL.md`.

## Powered By

- **Playwright CLI** — `npx playwright test`, `codegen`, `show-report`, `show-trace`
- **Composable Skills** — Inspired by [obra/superpowers](https://github.com/obra/superpowers)
- **Anti-Rationalization** — Explicit guards against skipping TDD
- **Evidence Verification** — No claims without proof
