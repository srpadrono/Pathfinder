---
name: pathfinder
description: >
  TDD workflow for AI coding agents. Use whenever the user wants to build a feature,
  fix a bug with tests, or follow test-driven development. Enforces test-first discipline
  using an expedition metaphor with scouts (tests) and builders (implementation).
  Integrates with Playwright for E2E and Vitest for unit tests. Use this skill even if
  the user doesn't explicitly mention TDD — any feature request, bug fix, or code change
  benefits from the Pathfinder workflow.
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

**Platform adapters:**
- Claude Code: `.claude-plugin/hooks/hooks.json` auto-loads at session start
- Codex: `.codex/INSTALL.md` for native skill discovery

## Scripts

- `scripts/verify-expedition.sh` — Run at Report phase to compute quality score and generate `.pathfinder/report.json`

## Powered By

- **Playwright CLI** — `npx playwright test`, `codegen`, `show-report`, `show-trace`
- **Composable Skills** — Inspired by [obra/superpowers](https://github.com/obra/superpowers)
- **Anti-Rationalization** — Explicit guards against skipping TDD
- **Evidence Verification** — No claims without proof
