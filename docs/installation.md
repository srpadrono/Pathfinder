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

## Step 2: Set Up for Your Agent

### Claude Code

Add Pathfinder as a skill directory in your project's `CLAUDE.md` or global settings:

```bash
# Option A: Add to project (recommended)
echo '
## Pathfinder
Read ~/.pathfinder/skill/SKILL.md at session start.
When I say /map, /blaze, /scout, or /summit, read the matching skill from ~/.pathfinder/skill/references/.
Scripts are in ~/.pathfinder/skill/scripts/ and ~/.pathfinder/skill/scripts/.
' >> CLAUDE.md

# Option B: Global config (~/.claude/settings.json)
# Add to "skillPaths":
# "~/.pathfinder/skills"
```

Enable git hooks for phase enforcement:
```bash
cd your-project
git config core.hooksPath ~/.pathfinder/.githooks
```

### Codex (OpenAI)

Add to your project's `AGENTS.md` or `codex.md`:

```bash
echo '
## Pathfinder — UI Test Coverage
Read ~/.pathfinder/skill/SKILL.md at session start.
Commands: /map, /blaze, /scout, /summit
When invoked, read the matching skill from ~/.pathfinder/skill/references/{mapping,blazing,scouting,summiting}.md.
Scripts: ~/.pathfinder/skill/scripts/ and ~/.pathfinder/skill/scripts/
Run scripts with python3. All output JSON to stdout, errors to stderr.
' >> AGENTS.md
```

### OpenClaw

Symlink to the skills directory:
```bash
ln -s ~/.pathfinder $(npm root -g)/openclaw/skills/pathfinder
```

Pathfinder's `hooks/session-start` and `hooks/hooks.json` handle auto-loading.

### Cursor

Add to `.cursorrules` in your project root:

```bash
echo '
## Pathfinder — UI Test Coverage Mapping
When I say /map, /blaze, /scout, or /summit, read the matching skill:
- /map → ~/.pathfinder/skill/references/mapping.md
- /blaze → ~/.pathfinder/skill/references/blazing.md
- /scout → ~/.pathfinder/skill/references/scouting.md
- /summit → ~/.pathfinder/skill/references/summiting.md

Overview: ~/.pathfinder/skill/SKILL.md
Scripts: ~/.pathfinder/skill/scripts/ and ~/.pathfinder/skill/scripts/
All scripts take CLI args and output JSON to stdout.
' >> .cursorrules
```

### Windsurf / Codeium

Add to `.windsurfrules` in your project root:

```bash
echo '
## Pathfinder — UI Test Coverage Mapping
When I say /map, /blaze, /scout, or /summit, read the matching skill:
- /map → ~/.pathfinder/skill/references/mapping.md
- /blaze → ~/.pathfinder/skill/references/blazing.md
- /scout → ~/.pathfinder/skill/references/scouting.md
- /summit → ~/.pathfinder/skill/references/summiting.md

Overview: ~/.pathfinder/skill/SKILL.md
Scripts: ~/.pathfinder/skill/scripts/ and ~/.pathfinder/skill/scripts/
' >> .windsurfrules
```

### Aider

Add to `.aider.conf.yml`:

```yaml
read:
  - ~/.pathfinder/skill/SKILL.md
```

Then reference skills manually when needed:
```
/read ~/.pathfinder/skill/references/mapping.md
```

### Any Other Agent

If your agent reads markdown instructions, add this to whatever config file it uses:

```markdown
## Pathfinder — UI Test Coverage

I have Pathfinder installed at ~/.pathfinder. It maps user journeys and generates UI tests.

Commands:
- /map — Read ~/.pathfinder/skill/references/mapping.md and follow it
- /blaze — Read ~/.pathfinder/skill/references/blazing.md and follow it
- /scout — Read ~/.pathfinder/skill/references/scouting.md and follow it
- /summit — Read ~/.pathfinder/skill/references/summiting.md and follow it

Scripts are CLI tools that take arguments and output JSON. Run with python3.
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
- **post-commit** — auto-regenerates diagrams when `journeys.json` changes
- **pre-push** — blocks direct push to main/master

## Verify Installation

Tell your agent `/map` — it should read the mapping skill and start discovering journeys.

## Updating

```bash
cd ~/.pathfinder && git pull origin main
```

### GitHub Copilot CLI

Copilot CLI uses `.github/instructions/pathfinder.instructions.md` — a lightweight instruction file that points to the globally installed tool:

```bash
bash ~/.pathfinder/install/setup-copilot.sh
```

Three setup methods:

1. **Environment variable** (recommended) — set `COPILOT_CUSTOM_INSTRUCTIONS_DIRS=~/.pathfinder/skill` in your shell profile. Copilot reads the AGENTS.md and references directly. Works across all repos, zero files copied.

2. **Per-repo instructions** — creates `.github/instructions/pathfinder.instructions.md` with `applyTo: "**"` frontmatter. Good for team repos where everyone should use Pathfinder.

3. **Global instructions** — appends to `~/.copilot/copilot-instructions.md`. Lightweight, always available.

All three methods point to `~/.pathfinder/skill/` — no code is copied into your project.
