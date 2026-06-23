# AGENTS.md

Instructions for AI coding agents working **on the Pathfinder repository**. (To
*use* Pathfinder in your own project, see [README.md](README.md).) This follows the
[AGENTS.md](https://agents.md) open standard and is read by Codex, Gemini CLI,
Cursor, and others.

## What this repo is

Pathfinder is an **Agent Skill**: it maps user journeys in a codebase, visualizes UI
test coverage as Mermaid diagrams, and generates framework-correct E2E tests. It
ships as five skills (`pathfinder`, `map`, `blaze`, `scout`, `summit`) plus Python
CLI scripts, packaged as a Claude Code plugin and as standard SKILL.md skills that
Codex and other agents discover from `~/.agents/skills/`.

## Setup

```bash
python3 -m pip install -r requirements-dev.txt   # pytest, ruff, jsonschema, Pillow
```

## Build / test / lint commands

Run all of these before finishing a change — fix failures until green.

```bash
python3 -m pytest tests/ -v                       # unit + integration tests
ruff check skills/pathfinder/scripts/ tests/ evals/scripts/ scripts/ mcp/   # lint
python3 scripts/validate-skill.py skills/pathfinder skills/map skills/blaze skills/scout skills/summit  # SKILL.md frontmatter compliance
python3 evals/scripts/validate_suite.py           # eval dataset schema + structure
python3 evals/scripts/run_evals.py --backend mock --runs 1   # eval harness plumbing smoke test
```

The full agent-graded evals (`run_evals.py --backend claude` → `grade_evals.py` →
`aggregate_benchmark.py`) need the `claude` CLI logged in or `ANTHROPIC_API_KEY`; run
them when you change skill behavior. See [evals/README.md](evals/README.md).

## Conventions

- **Scripts** are Python 3, stdlib-only where possible. They print JSON to stdout,
  diagnostics to stderr, and exit non-zero on failure. Handle errors (no raw
  tracebacks to users); no magic constants without a comment explaining them.
- **Skill authoring** follows the Agent Skills open standard: `name` (= directory
  name, lowercase/hyphen) and `description` (third person, says *what* + *when*) are
  required; keep SKILL.md bodies under ~500 lines; put framework detail in
  `references/` (loaded on demand). `validate-skill.py` enforces this.
- **Config & data** are schema-backed: `skills/pathfinder/schema/config.schema.json`
  and `journeys.schema.json`. New config options go in the schema, get a default in
  `scripts/pathfinder_config.py`, and must be consumed by a script or documented for
  the agent — no dead options.
- **Evals are honest.** Never make a grader pass unconditionally. New behavior needs
  a discriminating expectation (one that fails for a wrong output). The aggregator
  flags non-discriminating assertions; take that seriously.
- **Terminology:** "journey" (an end-to-end user goal), "step", "screen", "tested
  status" (`true`/`false`/`"partial"`). Step ids are `PREFIX-NN`.

## PR instructions

- Title: `type: summary` (e.g. `fix: …`, `feat: …`, `docs: …`).
- Run the five commands above; all must pass. Don't commit `evals/runs/`.
- Update `CHANGELOG.md` and bump the version in `plugin.json`, `marketplace.json`,
  `package.json`, and each skill's `metadata.version` together.
