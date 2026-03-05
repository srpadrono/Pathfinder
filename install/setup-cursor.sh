#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"
TARGET="${PWD}/.cursorrules"

echo "🔧 Setting up Pathfinder for Cursor..."

if [ -f "$TARGET" ] && grep -q "Pathfinder" "$TARGET" 2>/dev/null; then
  echo "⚠️  Pathfinder already in .cursorrules"
else
  cat >> "$TARGET" << 'SNIPPET'

## Pathfinder — UI Test Coverage Mapping

Pathfinder is installed at ~/.pathfinder/skill. It maps user journeys, visualizes test coverage with Mermaid flowcharts, and generates framework-correct UI tests.

When I say /map, /blaze, /scout, or /summit, read the matching file and follow it:
- /map → Read ~/.pathfinder/skill/references/mapping.md
- /blaze → Read ~/.pathfinder/skill/references/blazing.md
- /scout → Read ~/.pathfinder/skill/references/scouting.md
- /summit → Read ~/.pathfinder/skill/references/summiting.md

Full overview: ~/.pathfinder/skill/SKILL.md
Scripts: ~/.pathfinder/skill/scripts/ (Python 3 CLIs, JSON output)
SNIPPET
  echo "✅ Added Pathfinder to $TARGET"
fi

echo ""
read -p "Enable Pathfinder git hooks? (y/n): " hooks
if [ "$hooks" = "y" ]; then
  git config core.hooksPath "$PATHFINDER_HOME/.githooks"
  echo "✅ Git hooks enabled"
fi

echo ""
echo "🧭 Done! Say: /map"
