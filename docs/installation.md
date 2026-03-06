# Installation

## Requirements

- Python 3
- Git
- Pillow *(optional, for visual regression)* — `pip install Pillow`

## Quick Install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/srpadrono/Pathfinder/main/install/install.sh)
```

This clones the repo to `~/.agents/pathfinder` and symlinks skills into `~/.agents/skills/`. If a legacy `~/.pathfinder` install exists, it is automatically migrated.

## Plugin Install (Claude Code)

```bash
claude plugin marketplace add srpadrono/Pathfinder
claude plugin install pathfinder
```

This registers the Pathfinder marketplace and installs the plugin with automatic skill discovery. No CLAUDE.md snippet needed.

## Manual Install

### 1. Clone

```bash
git clone https://github.com/srpadrono/Pathfinder.git ~/.agents/pathfinder
```

### 2. Symlink skills

```bash
ln -s ~/.agents/pathfinder/skills/pathfinder ~/.agents/skills/pathfinder
ln -s ~/.agents/pathfinder/skills/map ~/.agents/skills/map
ln -s ~/.agents/pathfinder/skills/blaze ~/.agents/skills/blaze
ln -s ~/.agents/pathfinder/skills/scout ~/.agents/skills/scout
ln -s ~/.agents/pathfinder/skills/summit ~/.agents/skills/summit
```

### 3. Add to your agent

#### Claude Code

Add this snippet to your project's `CLAUDE.md`:

```markdown
## Pathfinder — UI Test Coverage Mapping

Pathfinder is installed at ~/.agents/skills/pathfinder. It maps user journeys,
visualizes test coverage with Mermaid flowcharts, and generates framework-correct UI tests.

Commands: /map, /blaze, /scout, /summit — each is a skill that activates automatically.

Full overview: ~/.agents/skills/pathfinder/SKILL.md
Scripts: ~/.agents/skills/pathfinder/scripts/ (Python 3 CLIs, JSON output)
```

#### Codex (GitHub Copilot)

Add the same snippet to your project's `AGENTS.md`.

### 4. Initialize in your project

```bash
cd your-project
python3 ~/.agents/skills/pathfinder/scripts/pathfinder-init.py
```

### 5. Git hooks (optional)

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
| `journeys.json` not found | Run `pathfinder-init.py` first |
| Git hooks not firing | `git config core.hooksPath` should show `~/.agents/pathfinder/.githooks` |
