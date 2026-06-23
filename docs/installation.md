# Installation

Pathfinder is a standard [Agent Skill](https://agentskills.io). Three install paths
— pick one; they install the same skills.

## Requirements

- Python 3 (runs all scripts)
- Git
- Pillow *(optional, for visual regression)* — `pip install Pillow`

## Option 1 — `npx skills` (any agent, recommended)

Installs into Claude Code, Codex, Gemini, Cursor, and more. The installer prompts
for which agents to target and whether to scope to one project or all projects.

```bash
npx skills add https://github.com/srpadrono/Pathfinder
```

If you get `npx: command not found`, install Node (`brew install node` on macOS;
if Homebrew is missing, install it from https://brew.sh), then re-run.

## Option 2 — Claude Code native plugin marketplace

```text
/plugin marketplace add srpadrono/Pathfinder
/plugin install pathfinder@pathfinder
```

## Option 3 — Self-contained installer (no Node)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/srpadrono/Pathfinder/main/install/install.sh)
```

This single command:
- Clones the repo to `~/.agents/pathfinder`
- Symlinks the skills into `~/.agents/skills/` — where **both Claude Code and Codex**
  auto-discover user-scoped skills
- Registers and installs the Claude Code plugin (if the `claude` CLI is available)
- Appends a usage pointer to `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` (if present)
- Migrates an existing `~/.pathfinder` install automatically

```bash
# pin a version / update / uninstall
bash <(curl -fsSL .../install.sh) --version v3.0.0
bash <(curl -fsSL .../install.sh) update
bash <(curl -fsSL .../install.sh) uninstall
```

Or just `git clone` the repo and point your agent at it however you like.

## How each agent discovers Pathfinder

| Agent | Discovery |
|-------|-----------|
| Claude Code | Plugin (via marketplace) or `~/.claude/skills/` |
| Codex | `~/.agents/skills/` (user) or `.agents/skills/` (repo) — same SKILL.md format |
| Gemini CLI / others | `AGENTS.md` + the Agent Skills standard |

## Git Hooks (optional)

```bash
git config core.hooksPath ~/.agents/pathfinder/.githooks
```

Enables: `journeys.json` validation on commit, auto-regenerate flowcharts, and a
block on direct pushes to `main`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3: command not found` | `brew install python` (macOS) or `sudo apt install python3` |
| `npx: command not found` | `brew install node`, then re-run (install Homebrew first if needed) |
| Agent ignores `/map` | Confirm the skill is installed and your instruction file has the Pathfinder pointer |
| `journeys.json` not found | Run `/map` first |
| Git hooks not firing | `git config core.hooksPath` should show `~/.agents/pathfinder/.githooks` |
| Install failed halfway | Re-run the installer — it cleans up and retries |
