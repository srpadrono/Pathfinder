# Pathfinder Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix the verified correctness bugs in Pathfinder's path contract, diagram generation, and aggregate output while adding regression coverage for each case.

**Architecture:** Treat `<testDir>/pathfinder/` as the canonical artifact location across scripts, hooks, and package commands. Rebuild decision-tree generation around actual step sequences instead of shared-root assumptions, and namespace aggregated journeys by module so monorepo output remains collision-free.

**Tech Stack:** Python 3 CLI scripts, shell hooks, npm package metadata, repo self-tests.

---

### Task 1: Lock In Diagram Regressions

**Files:**
- Modify: `tests/test_generate_diagrams.py`
- Test: `tests/test_generate_diagrams.py`

**Step 1: Write the failing tests**

Add scenarios for:
- multiple independent journey roots in the combined decision tree
- filename-only `--output` paths

**Step 2: Run tests to verify they fail**

Run: `python3 tests/test_generate_diagrams.py`
Expected: failures proving the current root-merging and output-path behavior is broken.

**Step 3: Write minimal implementation**

Update `skills/pathfinder/scripts/generate-diagrams.py` to:
- build a forest/graph from actual step chains
- preserve unrelated entry points
- safely handle `--output blazes.md`

**Step 4: Run tests to verify they pass**

Run: `python3 tests/test_generate_diagrams.py`
Expected: PASS

### Task 2: Lock In Canonical Pathfinder Paths

**Files:**
- Modify: `tests/test_generate_ui_test.py`
- Modify: `skills/pathfinder/scripts/generate-ui-test.py`
- Modify: `.githooks/pre-commit`
- Modify: `package.json`

**Step 1: Write the failing tests**

Add scenarios for:
- reading config from `<testDir>/pathfinder/config.json`
- appending into semicolon-terminated `describe` blocks

**Step 2: Run tests to verify they fail**

Run: `python3 tests/test_generate_ui_test.py`
Expected: FAIL on canonical path discovery and append placement.

**Step 3: Write minimal implementation**

Update the generator to locate canonical config files and robustly insert into common JS/TS block endings. Align hooks and npm commands with the same artifact location.

**Step 4: Run tests to verify they pass**

Run: `python3 tests/test_generate_ui_test.py`
Expected: PASS

### Task 3: Lock In Aggregate Namespacing

**Files:**
- Modify: `tests/test_aggregate.py`
- Modify: `skills/pathfinder/scripts/aggregate.py`

**Step 1: Write the failing test**

Add a two-module scenario with overlapping journey and step IDs and assert the merged JSON/output remains distinct.

**Step 2: Run test to verify it fails**

Run: `python3 tests/test_aggregate.py`
Expected: FAIL due to merged ID collisions.

**Step 3: Write minimal implementation**

Namespace merged journey and step IDs by module in aggregate mode while preserving original metadata for display.

**Step 4: Run test to verify it passes**

Run: `python3 tests/test_aggregate.py`
Expected: PASS

### Task 4: Verify End-to-End Quality Bar

**Files:**
- Modify: `README.md`
- Modify: `docs/installation.md`
- Modify: `skills/pathfinder/references/ui-testing.md`

**Step 1: Update docs**

Replace stale `.pathfinder` references with the canonical `<testDir>/pathfinder/` contract and note the supported command behavior.

**Step 2: Run repo verification**

Run:
- `python3 tests/test_generate_diagrams.py`
- `python3 tests/test_generate_ui_test.py`
- `python3 tests/test_aggregate.py`
- `npm test`

Expected: PASS
