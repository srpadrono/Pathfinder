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
- Migrates existing `~/.pathfinder` installs automatically

For **Claude Code** users, that's it — the plugin handles everything.

For **Codex, Gemini CLI, Cursor**, add this snippet to your project's `CLAUDE.md` or `AGENTS.md`:

```markdown
## Pathfinder — UI Test Coverage Mapping

Pathfinder is installed at ~/.agents/skills/pathfinder. It maps user journeys,
visualizes test coverage with Mermaid flowcharts, and generates framework-correct UI tests.

Commands: /map, /blaze, /scout, /summit — each is a skill that activates automatically.

Full overview: ~/.agents/skills/pathfinder/SKILL.md
Scripts: ~/.agents/skills/pathfinder/scripts/ (Python 3 CLIs, JSON output)
```

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

Removes the repo, symlinks, and Claude Code plugin registration.

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
