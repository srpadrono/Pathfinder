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
Read ~/.pathfinder/skills/using-pathfinder/SKILL.md at session start.
When I say /map, /blaze, /scout, or /summit, read the matching skill from ~/.pathfinder/skills/.
Scripts are in ~/.pathfinder/scripts/ and ~/.pathfinder/skills/*/scripts/.
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
Read ~/.pathfinder/skills/using-pathfinder/SKILL.md at session start.
Commands: /map, /blaze, /scout, /summit
When invoked, read the matching skill from ~/.pathfinder/skills/{mapping,blazing,scouting,summiting}/SKILL.md.
Scripts: ~/.pathfinder/scripts/ and ~/.pathfinder/skills/*/scripts/
Run scripts with python3. All output JSON to stdout, errors to stderr.
' >> AGENTS.md
```

### OpenClaw

Symlink to the skills directory:
```bash
ln -s ~/.pathfinder ~/.npm-global/lib/node_modules/openclaw/skills/pathfinder
```

Pathfinder's `hooks/session-start` and `hooks/hooks.json` handle auto-loading.

### Cursor

Add to `.cursorrules` in your project root:

```bash
echo '
## Pathfinder — UI Test Coverage Mapping
When I say /map, /blaze, /scout, or /summit, read the matching skill:
- /map → ~/.pathfinder/skills/mapping/SKILL.md
- /blaze → ~/.pathfinder/skills/blazing/SKILL.md
- /scout → ~/.pathfinder/skills/scouting/SKILL.md
- /summit → ~/.pathfinder/skills/summiting/SKILL.md

Overview: ~/.pathfinder/skills/using-pathfinder/SKILL.md
Scripts: ~/.pathfinder/scripts/ and ~/.pathfinder/skills/*/scripts/
All scripts take CLI args and output JSON to stdout.
' >> .cursorrules
```

### Windsurf / Codeium

Add to `.windsurfrules` in your project root:

```bash
echo '
## Pathfinder — UI Test Coverage Mapping
When I say /map, /blaze, /scout, or /summit, read the matching skill:
- /map → ~/.pathfinder/skills/mapping/SKILL.md
- /blaze → ~/.pathfinder/skills/blazing/SKILL.md
- /scout → ~/.pathfinder/skills/scouting/SKILL.md
- /summit → ~/.pathfinder/skills/summiting/SKILL.md

Overview: ~/.pathfinder/skills/using-pathfinder/SKILL.md
Scripts: ~/.pathfinder/scripts/ and ~/.pathfinder/skills/*/scripts/
' >> .windsurfrules
```

### Aider

Add to `.aider.conf.yml`:

```yaml
read:
  - ~/.pathfinder/skills/using-pathfinder/SKILL.md
```

Then reference skills manually when needed:
```
/read ~/.pathfinder/skills/mapping/SKILL.md
```

### Any Other Agent

If your agent reads markdown instructions, add this to whatever config file it uses:

```markdown
## Pathfinder — UI Test Coverage

I have Pathfinder installed at ~/.pathfinder. It maps user journeys and generates UI tests.

Commands:
- /map — Read ~/.pathfinder/skills/mapping/SKILL.md and follow it
- /blaze — Read ~/.pathfinder/skills/blazing/SKILL.md and follow it
- /scout — Read ~/.pathfinder/skills/scouting/SKILL.md and follow it
- /summit — Read ~/.pathfinder/skills/summiting/SKILL.md and follow it

Scripts are CLI tools that take arguments and output JSON. Run with python3.
```

## Step 3: Initialize in Your Project

```bash
cd your-project
python3 ~/.pathfinder/scripts/pathfinder-init.py
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
