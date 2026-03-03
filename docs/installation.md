# Installation

## Requirements

- Git
- Python 3 (for JSON parsing in scripts)
- `gh` CLI (for PR creation in report phase)

## OpenClaw

```bash
git clone https://github.com/srhenrybot-hub/superpowers.git ~/.pathfinder
ln -s ~/.pathfinder ~/.npm-global/lib/node_modules/openclaw/skills/pathfinder
```

## Any Project (Git Hooks)

```bash
cd your-project
git config core.hooksPath /path/to/pathfinder/.githooks
```

Activates: pre-push (blocks main), pre-commit (phase ordering), post-commit (state sync).

## Verify

Type `/survey` in a conversation. The agent should invoke `pathfinder:surveying`.

## Updating

```bash
cd ~/.pathfinder && git pull origin main
```
