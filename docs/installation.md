# Installation

## Requirements

- Python 3
- Git
- Pillow *(optional, for visual regression)* — `pip install Pillow`

## Install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/srpadrono/Pathfinder/main/install/install.sh)
```

This single command:
- Clones the repo to `~/.agents/pathfinder`
- Symlinks skills into `~/.agents/skills/`
- Registers and installs the Claude Code plugin (if `claude` CLI is available)
- Injects the Pathfinder snippet into `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` (if those directories exist)
- Migrates existing `~/.pathfinder` installs automatically

That's it — no manual configuration needed.

### Pin a specific version

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/srpadrono/Pathfinder/main/install/install.sh) --version v2.1.0
```

## Updating

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/srpadrono/Pathfinder/main/install/install.sh) update
```

Or update and pin to a specific version:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/srpadrono/Pathfinder/main/install/install.sh) update --version v2.2.0
```

## Uninstalling

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/srpadrono/Pathfinder/main/install/install.sh) uninstall
```

Removes the repo, symlinks, Claude Code plugin, and agent instruction snippets.

## Git Hooks (optional)

```bash
git config core.hooksPath ~/.agents/pathfinder/.githooks
```

Enables: `journeys.json` validation on commit, auto-regenerate flowcharts, block direct push to main.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3: command not found` | `brew install python` (macOS) or `sudo apt install python3` |
| Agent ignores `/map` | Check instruction file contains the Pathfinder snippet |
| `journeys.json` not found | Run `/map` first |
| Git hooks not firing | `git config core.hooksPath` should show `~/.agents/pathfinder/.githooks` |
| Install failed halfway | Re-run the installer — it cleans up and retries |
