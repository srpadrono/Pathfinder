#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"
REPO="https://github.com/srpadrono/Pathfinder.git"

SNIPPET='## Pathfinder — UI Test Coverage Mapping

Pathfinder is installed at ~/.pathfinder/skill. It maps user journeys, visualizes test coverage with Mermaid flowcharts, and generates framework-correct UI tests.

When I say /map, /blaze, /scout, or /summit, read the matching file and follow it:
- /map → Read ~/.pathfinder/skill/references/mapping.md
- /blaze → Read ~/.pathfinder/skill/references/blazing.md
- /scout → Read ~/.pathfinder/skill/references/scouting.md
- /summit → Read ~/.pathfinder/skill/references/summiting.md

Full overview: ~/.pathfinder/skill/SKILL.md
Scripts: ~/.pathfinder/skill/scripts/ (Python 3 CLIs, JSON output)'

echo "🧭 Pathfinder Installer"
echo ""

# Step 1: Install
if [ -d "$PATHFINDER_HOME" ]; then
  echo "📦 Updating..."
  cd "$PATHFINDER_HOME" && git pull origin main --quiet
  cd - > /dev/null
else
  echo "📦 Installing..."
  git clone --quiet "$REPO" "$PATHFINDER_HOME"
fi
echo "✅ Installed at $PATHFINDER_HOME"

# Step 2: Pick agent
echo ""
echo "Which AI coding agent?"
echo "  1) Claude Code         → CLAUDE.md"
echo "  2) GitHub Copilot/Codex → AGENTS.md"
echo "  3) Cursor              → .cursorrules"
echo "  4) Windsurf            → .windsurfrules"
echo "  5) Aider               → .aider.conf.yml"
echo "  6) OpenClaw            → symlink"
echo "  7) Other               → prints snippet"
echo ""
read -p "Select (1-7): " choice

case $choice in
  1) TARGET="CLAUDE.md" ;;
  2) TARGET="AGENTS.md" ;;
  3) TARGET=".cursorrules" ;;
  4) TARGET=".windsurfrules" ;;
  5) TARGET=".aider.conf.yml" ;;
  6)
    SKILL_DIR="$(npm root -g 2>/dev/null)/openclaw/skills"
    if [ -d "$SKILL_DIR" ]; then
      ln -sf "$PATHFINDER_HOME/skill" "$SKILL_DIR/pathfinder"
      echo "✅ Symlinked to $SKILL_DIR/pathfinder"
    else
      echo "❌ OpenClaw not found. Symlink manually:"
      echo "   ln -s ~/.pathfinder/skill <openclaw-skills-dir>/pathfinder"
    fi
    TARGET=""
    ;;
  7)
    echo ""
    echo "Add this to your agent's instruction file:"
    echo ""
    echo "$SNIPPET"
    TARGET=""
    ;;
  *) echo "Invalid choice"; exit 1 ;;
esac

if [ -n "${TARGET:-}" ]; then
  if [ -f "$TARGET" ] && grep -q "Pathfinder" "$TARGET" 2>/dev/null; then
    echo "⚠️  Pathfinder already in $TARGET"
  else
    echo "" >> "$TARGET"
    echo "$SNIPPET" >> "$TARGET"
    echo "✅ Added to $TARGET"
  fi
fi

# Step 3: Git hooks
echo ""
read -p "Enable git hooks? (y/n): " hooks
if [ "$hooks" = "y" ]; then
  git config core.hooksPath "$PATHFINDER_HOME/.githooks"
  echo "✅ Git hooks enabled"
fi

# Step 4: Verify
echo ""
if python3 -c "import json" 2>/dev/null; then
  echo "✅ Python 3 available"
else
  echo "⚠️  Python 3 not found"
fi

echo ""
echo "🧭 Next: cd your-project && python3 ~/.pathfinder/skill/scripts/pathfinder-init.py"
echo "   Then: /map"
