#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"
SNIPPET='
## Pathfinder — UI Test Coverage Mapping
Read ~/.pathfinder/skill/SKILL.md at session start.
When I say /map, /blaze, /scout, or /summit, read the matching skill:
- /map → ~/.pathfinder/skill/references/mapping.md
- /blaze → ~/.pathfinder/skill/references/blazing.md
- /scout → ~/.pathfinder/skill/references/scouting.md
- /summit → ~/.pathfinder/skill/references/summiting.md
Scripts: ~/.pathfinder/skill/scripts/ and ~/.pathfinder/skill/scripts/
'

echo "🔧 Setting up for Claude Code..."
echo ""
echo "Choose setup method:"
echo "  1) Add to project CLAUDE.md (recommended)"
echo "  2) Add to global ~/.claude/settings.json"
echo ""
read -p "Select (1-2): " method

if [ "$method" = "1" ]; then
  TARGET="${PWD}/CLAUDE.md"
  if [ -f "$TARGET" ] && grep -q "Pathfinder" "$TARGET" 2>/dev/null; then
    echo "⚠️  Pathfinder already in CLAUDE.md"
  else
    echo "$SNIPPET" >> "$TARGET"
    echo "✅ Added to $TARGET"
  fi
elif [ "$method" = "2" ]; then
  SETTINGS="${HOME}/.claude/settings.json"
  mkdir -p "$(dirname "$SETTINGS")"
  if [ -f "$SETTINGS" ]; then
    if grep -q "pathfinder" "$SETTINGS" 2>/dev/null; then
      echo "⚠️  Pathfinder already in settings.json"
    else
      echo "Add this to your skillPaths array in $SETTINGS:"
      echo '  "~/.pathfinder/skills"'
      echo ""
      echo "(Manually edit the file — JSON merging is fragile in bash)"
    fi
  else
    cat > "$SETTINGS" << SETTINGS
{
  "skillPaths": ["~/.pathfinder/skills"]
}
SETTINGS
    echo "✅ Created $SETTINGS with Pathfinder skills"
  fi
fi

# Git hooks
echo ""
read -p "Enable git hooks in current project? (y/n): " hooks
if [ "$hooks" = "y" ]; then
  git config core.hooksPath "$PATHFINDER_HOME/.githooks"
  echo "✅ Git hooks enabled"
fi

echo ""
echo "🧭 Done! Tell Claude: /map"
