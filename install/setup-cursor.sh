#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"
SNIPPET='
## Pathfinder — UI Test Coverage Mapping
When I say /map, /blaze, /scout, or /summit, read the matching skill:
- /map → ~/.pathfinder/skills/mapping/SKILL.md
- /blaze → ~/.pathfinder/skills/blazing/SKILL.md
- /scout → ~/.pathfinder/skills/scouting/SKILL.md
- /summit → ~/.pathfinder/skills/summiting/SKILL.md
Overview: ~/.pathfinder/skills/using-pathfinder/SKILL.md
Scripts: ~/.pathfinder/scripts/ and ~/.pathfinder/skills/*/scripts/
All scripts take CLI args and output JSON to stdout.
'

echo "🔧 Setting up for Cursor..."

TARGET="${PWD}/.cursorrules"
if [ -f "$TARGET" ] && grep -q "Pathfinder" "$TARGET" 2>/dev/null; then
  echo "⚠️  Pathfinder already in .cursorrules"
else
  echo "$SNIPPET" >> "$TARGET"
  echo "✅ Added to $TARGET"
fi

read -p "Enable git hooks in current project? (y/n): " hooks
if [ "$hooks" = "y" ]; then
  git config core.hooksPath "$PATHFINDER_HOME/.githooks"
  echo "✅ Git hooks enabled"
fi

echo ""
echo "🧭 Done! Tell Cursor: /map"
