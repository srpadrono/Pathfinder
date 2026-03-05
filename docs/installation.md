# Installation

## Requirements

- Python 3
- Git
- Pillow *(optional, for visual regression)* — `pip install Pillow`

## Quick Install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/srpadrono/Pathfinder/main/install/install.sh)
```

This clones Pathfinder to `~/.pathfinder` and adds instructions to your agent's config file.

## Manual Install

### 1. Clone

```bash
git clone https://github.com/srpadrono/Pathfinder.git ~/.pathfinder
```

### 2. Add to your agent

#### Claude Code

Add this snippet to your project's `CLAUDE.md`:

```markdown
## Pathfinder — UI Test Coverage Mapping

Pathfinder is installed at ~/.pathfinder/skill. It maps user journeys, visualizes
test coverage with Mermaid flowcharts, and generates framework-correct UI tests.

When I say /map, /blaze, /scout, or /summit, read the matching file and follow it:
- /map → Read ~/.pathfinder/skill/references/mapping.md
- /blaze → Read ~/.pathfinder/skill/references/blazing.md
- /scout → Read ~/.pathfinder/skill/references/scouting.md
- /summit → Read ~/.pathfinder/skill/references/summiting.md

Full overview: ~/.pathfinder/skill/SKILL.md
Scripts: ~/.pathfinder/skill/scripts/ (Python 3 CLIs, JSON output)
```

#### Codex (GitHub Copilot)

Add the same snippet to your project's `AGENTS.md`.

### 3. Initialize in your project

```bash
cd your-project
python3 ~/.pathfinder/skill/scripts/pathfinder-init.py
```

### 4. Git hooks (optional)

```bash
git config core.hooksPath ~/.pathfinder/.githooks
```

Enables: `journeys.json` validation on commit, auto-regenerate flowcharts, block direct push to main.

## Updating

```bash
cd ~/.pathfinder && git pull
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3: command not found` | `brew install python` (macOS) or `sudo apt install python3` |
| Agent ignores `/map` | Check instruction file contains the Pathfinder snippet |
| `journeys.json` not found | Run `pathfinder-init.py` first |
| Git hooks not firing | `git config core.hooksPath` should show `~/.pathfinder/.githooks` |
