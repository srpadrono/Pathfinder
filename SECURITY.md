# Security

## Reporting a vulnerability

Please report security issues privately via [GitHub Security Advisories](https://github.com/srpadrono/Pathfinder/security/advisories/new)
(or open a minimal issue asking for a private channel — do not post exploit details
publicly). We aim to acknowledge within a few days.

## What you're running

Agent Skills can execute code, so it's reasonable to audit before installing. For
Pathfinder specifically:

- **Bundled scripts are Python 3, standard-library only**, and live in
  `skills/pathfinder/scripts/`. They read your project files and write Pathfinder
  artifacts (`journeys.json`, `blazes.md`, generated test stubs). They do **not**
  make network calls and do **not** transmit your code anywhere.
- **The eval harness** (`evals/`) is the only part that invokes an LLM, and only when
  you explicitly run the agent-graded commands (`run_evals.py --backend claude`,
  `grade_evals.py`). Those shell out to your local `claude`/`codex` CLI; nothing runs
  automatically and nothing runs in CI.
- **The installer** (`install/install.sh`) clones this repo, symlinks skills into
  `~/.agents/skills/`, and (optionally) registers the Claude Code plugin. Read it
  before piping to bash — `--version` lets you pin a reviewed tag.
- **Generated tests** are skeletons with `TODO`s; review them like any code before
  running against real environments or credentials.

## Scope

This project follows the principle of least surprise: a skill's behavior should
match what its description says. If you find behavior that does something a user
wouldn't expect from the docs, treat it as a security issue and report it.
