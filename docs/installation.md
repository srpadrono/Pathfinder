# Installation

## Requirements

- Python 3
- Git
- A UI test framework (auto-detected)
- Pillow *(optional, for visual regression)* — `pip install Pillow`

## Step 1: Clone Pathfinder

```bash
git clone https://github.com/srpadrono/Pathfinder.git ~/.pathfinder
```

Or use the interactive installer:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/srpadrono/Pathfinder/main/install/install.sh)
```

## Step 2: Set Up for Your Agent

Every AI coding agent reads an instruction file from your project root. Pathfinder adds its instructions to that file.

Run the setup script for your platform:

```bash
bash ~/.pathfinder/install/setup-<platform>.sh
```

| Platform | Script | Writes to |
|----------|--------|-----------|
| Claude Code | `setup-claude-code.sh` | `CLAUDE.md` |
| GitHub Copilot | `setup-copilot.sh` | `AGENTS.md` |
| Codex | `setup-codex.sh` | `AGENTS.md` |
| Cursor | `setup-cursor.sh` | `.cursorrules` |
| Windsurf | `setup-windsurf.sh` | `.windsurfrules` |
| Aider | `setup-aider.sh` | `.aider.conf.yml` |
| OpenClaw | `setup-openclaw.sh` | Skills symlink |
| Other | `setup-generic.sh` | Prints snippet to copy |

All scripts add the same content — Pathfinder commands mapped to `~/.pathfinder/skill/` references and scripts. The only difference is the target file name.

### Manual Setup

If you prefer, add this to your agent's instruction file (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, etc.):

```markdown
## Pathfinder — UI Test Coverage Mapping

Pathfinder is installed at ~/.pathfinder/skill.

When I say /map, /blaze, /scout, or /summit, read the matching file and follow it:
- /map → ~/.pathfinder/skill/references/mapping.md
- /blaze → ~/.pathfinder/skill/references/blazing.md
- /scout → ~/.pathfinder/skill/references/scouting.md
- /summit → ~/.pathfinder/skill/references/summiting.md

Full overview: ~/.pathfinder/skill/SKILL.md
Scripts: ~/.pathfinder/skill/scripts/ (Python 3 CLIs, JSON output)
```

## Step 3: Initialize in Your Project

```bash
cd your-project
python3 ~/.pathfinder/skill/scripts/pathfinder-init.py
```

This auto-detects your UI framework and creates `.pathfinder/config.json`.

## Step 4: Enable Git Hooks (Optional)

```bash
cd your-project
git config core.hooksPath ~/.pathfinder/.githooks
```

This enables:
- **pre-commit** — validates `journeys.json` format
- **post-commit** — auto-regenerates flowcharts when `journeys.json` changes
- **pre-push** — blocks direct push to main/master

## Verify

Tell your agent `/map` — it should read the mapping reference and start discovering journeys.

## Updating

```bash
cd ~/.pathfinder && git pull origin main
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python3: command not found` | Install Python 3: `brew install python` (macOS) or `sudo apt install python3` (Linux) |
| Agent doesn't recognise `/map` | Check the instruction file exists and contains the Pathfinder section |
| `journeys.json` not found | Run `pathfinder-init.py` in your project first |
| Permission denied on install | `chmod +x ~/.pathfinder/install/*.sh` |
| Git hooks not firing | Check `git config core.hooksPath` shows `~/.pathfinder/.githooks` |
