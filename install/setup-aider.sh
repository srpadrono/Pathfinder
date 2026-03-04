#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"

echo "🔧 Setting up for Aider..."

TARGET="${PWD}/.aider.conf.yml"
if [ -f "$TARGET" ] && grep -q "pathfinder" "$TARGET" 2>/dev/null; then
  echo "⚠️  Pathfinder already in .aider.conf.yml"
else
  cat >> "$TARGET" << AIDER

# Pathfinder — UI Test Coverage Mapping
read:
  - ~/.pathfinder/skills/using-pathfinder/SKILL.md
AIDER
  echo "✅ Added to $TARGET"
  echo ""
  echo "To load specific skills in Aider, run:"
  echo "  /read ~/.pathfinder/skills/mapping/SKILL.md"
  echo "  /read ~/.pathfinder/skills/blazing/SKILL.md"
  echo "  /read ~/.pathfinder/skills/scouting/SKILL.md"
  echo "  /read ~/.pathfinder/skills/summiting/SKILL.md"
fi

echo ""
echo "🧭 Done!"
