# Installation

## Requirements

- Python 3
- Git
- Pillow *(optional, for visual regression)* — `pip install Pillow`

## Claude Code Plugin (recommended)

```bash
claude plugin marketplace add srpadrono/Pathfinder
claude plugin install pathfinder
```

That's it. The plugin handles skills, hooks, and agent configuration automatically.

## One-liner (Codex, Gemini CLI, Cursor, etc.)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/srpadrono/Pathfinder/main/install/install.sh)
```

This clones the repo to `~/.agents/pathfinder`, symlinks skills into `~/.agents/skills/`, and registers the Claude Code plugin if the CLI is available. Existing `~/.pathfinder` installs are migrated automatically.

After installing, add this snippet to your project's `CLAUDE.md` (or `AGENTS.md` for Codex):

```markdown
## Pathfinder — UI Test Coverage Mapping

Pathfinder is installed at ~/.agents/skills/pathfinder. It maps user journeys,
visualizes test coverage with Mermaid flowcharts, and generates framework-correct UI tests.

Commands: /map, /blaze, /scout, /summit — each is a skill that activates automatically.

Full overview: ~/.agents/skills/pathfinder/SKILL.md
Scripts: ~/.agents/skills/pathfinder/scripts/ (Python 3 CLIs, JSON output)
```

## Git Hooks (optional)

```bash
git config core.hooksPath ~/.agents/pathfinder/.githooks
```

Enables: `journeys.json` validation on commit, auto-regenerate flowcharts, block direct push to main.

## Updating

```bash
cd ~/.agents/pathfinder && git pull
```

## Uninstalling

```bash
rm -rf ~/.agents/pathfinder
rm ~/.agents/skills/{pathfinder,map,blaze,scout,summit}
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3: command not found` | `brew install python` (macOS) or `sudo apt install python3` |
| Agent ignores `/map` | Check instruction file contains the Pathfinder snippet |
| `journeys.json` not found | Run `/map` first |
| Git hooks not firing | `git config core.hooksPath` should show `~/.agents/pathfinder/.githooks` |
