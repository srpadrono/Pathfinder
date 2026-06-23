# Contributing to Pathfinder

Thanks for helping make Pathfinder better. This is an [Agent Skill](https://agentskills.io)
repo; most "code" is Python CLIs plus carefully-written SKILL.md instructions.

## Setup

```bash
python3 -m pip install -r requirements-dev.txt
```

## The checks (run all before opening a PR)

```bash
python3 -m pytest tests/ -v                                  # tests
ruff check skills/pathfinder/scripts/ tests/ evals/scripts/ scripts/ mcp/   # lint
python3 scripts/validate-skill.py skills/pathfinder skills/map skills/blaze skills/scout skills/summit
python3 evals/scripts/validate_suite.py                      # eval dataset
python3 evals/scripts/run_evals.py --backend mock --runs 1   # eval plumbing
```

CI runs exactly these. The agent-graded evals (`run_evals.py --backend claude` →
`grade_evals.py` → `aggregate_benchmark.py`) need credentials — run them when you
change skill behavior and paste the benchmark delta into your PR.

## Conventions

- **Scripts**: Python 3, stdlib-first, JSON to stdout / diagnostics to stderr,
  non-zero exit on failure, no raw tracebacks shown to users, no undocumented magic
  numbers. Add a test for every script change (`tests/`).
- **Skills**: follow the Agent Skills open standard. `name` must equal the directory
  name; `description` is third person and says *what* + *when*; keep SKILL.md bodies
  under ~500 lines and push framework detail into `references/`. `validate-skill.py`
  enforces the rules.
- **Config / data**: schema-backed. A new config option goes in
  `skills/pathfinder/schema/config.schema.json`, gets a default in
  `scripts/pathfinder_config.py`, and must actually be consumed — no dead options.
- **Evals**: never make a grader pass unconditionally. New behavior gets a
  *discriminating* expectation (fails for a wrong output). Respect the
  non-discriminating-assertion warnings from the aggregator.

## Adding a framework

1. Add a `references/<framework>.md` guide (selectors, waits, run command, template).
2. Add detection to `scripts/detect-ui-framework.py` + a test.
3. Add a template to `scripts/generate-ui-test.py` + a test.
4. Add a triggering / output-quality eval case if it's a major surface.

## Pull requests

- Title `type: summary` (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`).
- All checks green. Don't commit `evals/runs/`.
- Update `CHANGELOG.md`, and bump the version in `plugin.json`, `marketplace.json`,
  `package.json`, and each skill's `metadata.version` together.

By contributing you agree your work is licensed under the repo's [MIT License](LICENSE).
