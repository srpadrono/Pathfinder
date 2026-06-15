# Changelog

All notable changes to Pathfinder are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] — 2026-06-14

A best-in-class pass: honest evals, full configurability, and first-class
cross-agent support.

### Added
- **Honest, compliant eval suite** (`evals/`) modeled on Anthropic's skill-creator
  and OpenAI's skill-eval methodology:
  - Output-quality evals run **A/B** (with skill vs. baseline agent), graded by an
    **LLM judge** (no partial credit, evidence-cited) across multiple runs with
    **mean ± stddev** and **skill-lift** reporting.
  - An aggregator that automatically flags **non-discriminating assertions** and
    high-variance cases.
  - A **triggering** eval (20 queries, half near-miss negatives) with a held-out
    test split; reports accuracy / precision / recall.
  - JSON Schemas + `validate_suite.py` so CI gates a well-formed dataset, plus a
    `mock` backend for offline plumbing smoke tests.
  - A **description optimizer loop** (`run_loop.py`) that tunes the skill's
    `description` against the triggering eval, selecting by held-out test score.
- **MCP server** (`mcp/server.py`): a dependency-free stdio MCP server exposing the
  deterministic tools (`detect_ui_framework`, `scan_test_coverage`, `coverage_score`,
  `validate_journeys`, `generate_diagrams`) to any MCP client; auto-registered with
  the Claude Code plugin via `.mcp.json`.
- **Configurability**: `config.json` and `journeys.json` now ship JSON Schemas
  (`skills/pathfinder/schema/`) with `$schema` autocomplete. New config options —
  coverage `thresholds` / `failUnder` / `countPartialAsTested`, `ignore` globs,
  `commands.test`, and `selectors` — wired into the scripts via
  `scripts/pathfinder_config.py`.
- **Cross-agent support**: root `AGENTS.md` (open standard), Codex presentation
  metadata (`skills/pathfinder/agents/openai.yaml`), and a documented `npx skills`
  install path alongside the native plugin and the self-contained installer.
- **Skill-frontmatter validator** (`scripts/validate-skill.py`) enforcing the Agent
  Skills open standard; gated in CI.
- `license` + `metadata` frontmatter on all five skills.

### Changed
- `coverage-score.py` is now a clean reporting tool: it exits 0 by default and gates
  only when you ask (`--fail-under` or `coverage.failUnder`), instead of always
  exiting non-zero below 50%.
- Coverage thresholds and status colors are read from config (no more hardcoded
  80/50) in `coverage-score.py` and `generate-diagrams.py`.
- CI workflow now lints, validates skill frontmatter, validates the eval suite, runs
  tests, and smoke-tests the eval harness.

### Fixed
- **Multi-module aggregation bug**: `aggregate.py` wrote its merged journeys to the
  shared system temp dir, so the baseline `generate-diagrams.py` created there leaked
  across runs and intermittently swapped the decision-tree section for a before/after
  view. It now uses an isolated temp directory and a new `--no-baseline` flag.
- **Eval harness now actually exercises the skill.** Headless `claude -p` does not
  discover a temp project's `.claude/skills/`; the with-skill arm now loads the plugin
  via `--plugin-dir` (skills register as `pathfinder:<name>`) and pins the model, and
  the triggering detector matches the plugin-namespaced Skill invocation exactly
  (no more false positives from generic words like "map" in another tool's args).
- **Hardening pass** (from an adversarial multi-agent review): malformed/mis-typed
  `config.json` falls back to defaults instead of crashing any script; the MCP server
  uses correct JSON-RPC error codes (`-32601`/`-32602`), validates required args, and
  blocks CLI-flag injection through path arguments (`--` separator); `coverage-score.py`
  roots its config at the journeys file's project; `aggregate.py` propagates the diagram
  generator's exit code; the eval aggregator now reconciles each case's declared
  `discriminating` flag against observed data; and the git hooks no longer auto-stage
  files or block pushes based on the wrong branch.
- **Eval honesty under failure**: a backend session/usage limit or unavailable model
  now makes the runners and grader abort with a clear message, and the aggregator
  excludes ungraded runs — so a model outage is never reported as a 0% skill failure.
  `grade_evals.py` resumes incrementally (skips already-graded runs; `--regrade` to
  redo), so grading completes across usage windows without re-running the agent.
- **Triggering: description sharpened** after a real eval run showed perfect precision
  (no false triggers) but only 40% recall, missing mobile-framework, "write E2E tests",
  and "diagram" framings. The `description` now names those framings explicitly.

### Removed
- The previous eval harness, whose graders returned `passed: true` unconditionally
  and ran the bundled scripts directly instead of the agent — then reported a
  meaningless "100% pass rate." Replaced wholesale by the suite above.

## [2.x] — earlier

See the git history for 2.x (plugin packaging, installer hardening, decision-tree
diagrams, per-journey charts). Tags were not published for these.
