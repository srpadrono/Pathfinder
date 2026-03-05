#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"

# Step 1: Clone if needed
if [ ! -d "$PATHFINDER_HOME" ]; then
  echo "📥 Cloning Pathfinder..."
  git clone https://github.com/srpadrono/Pathfinder.git "$PATHFINDER_HOME"
else
  echo "✅ Pathfinder already installed at $PATHFINDER_HOME"
fi

# Step 2: Pick target file
echo ""
echo "Which AI coding agent are you using?"
echo "  1) Claude Code        → CLAUDE.md"
echo "  2) GitHub Copilot     → AGENTS.md"
echo "  3) Codex              → AGENTS.md"
echo "  4) Cursor             → .cursorrules"
echo "  5) Windsurf           → .windsurfrules"
echo "  6) Aider              → .aider.conf.yml"
echo "  7) OpenClaw           → Skills symlink"
echo "  8) Other / Manual"
echo ""
read -p "Select (1-8): " choice

SNIPPET='
## Pathfinder — UI Test Coverage Mapping

Pathfinder is installed at ~/.pathfinder/skill. It maps user journeys, visualizes test coverage with Mermaid flowcharts, and generates framework-correct UI tests.

When I say /map, /blaze, /scout, or /summit, read the matching file and follow it:
- /map → Read ~/.pathfinder/skill/references/mapping.md
- /blaze → Read ~/.pathfinder/skill/references/blazing.md
- /scout → Read ~/.pathfinder/skill/references/scouting.md
- /summit → Read ~/.pathfinder/skill/references/summiting.md

Full overview: ~/.pathfinder/skill/SKILL.md
Scripts: ~/.pathfinder/skill/scripts/ (Python 3 CLIs, JSON output)
'

case $choice in
  1) TARGET="CLAUDE.md" ;;
  2|3) TARGET="AGENTS.md" ;;
  4) TARGET=".cursorrules" ;;
  5) TARGET=".windsurfrules" ;;
  6) TARGET=".aider.conf.yml" ;;
  7)
    SKILL_DIR="$(npm root -g 2>/dev/null)/openclaw/skills"
    if [ -d "$SKILL_DIR" ]; then
      ln -sf "$PATHFINDER_HOME/skill" "$SKILL_DIR/pathfinder"
      echo "✅ Symlinked to $SKILL_DIR/pathfinder"
    else
      echo "❌ OpenClaw skills directory not found. Install OpenClaw first."
      exit 1
    fi
    TARGET=""
    ;;
  8)
    echo ""
    echo "Add this to your agent's instruction file:"
    echo "$SNIPPET"
    TARGET=""
    ;;
  *) echo "Invalid choice"; exit 1 ;;
esac

if [ -n "$TARGET" ]; then
  FULL_PATH="${PWD}/${TARGET}"
  if [ -f "$FULL_PATH" ] && grep -q "Pathfinder" "$FULL_PATH" 2>/dev/null; then
    echo "⚠️  Pathfinder already in $TARGET"
  else
    echo "$SNIPPET" >> "$FULL_PATH"
    echo "✅ Added Pathfinder to $TARGET"
  fi
fi

# Step 3: Git hooks
echo ""
read -p "Enable Pathfinder git hooks? (y/n): " hooks
if [ "$hooks" = "y" ]; then
  git config core.hooksPath "$PATHFINDER_HOME/.githooks"
  echo "✅ Git hooks enabled"
fi

echo ""
echo "🧭 Done! Say: /map"
