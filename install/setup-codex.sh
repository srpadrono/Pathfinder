#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"
SNIPPET='
## Pathfinder — UI Test Coverage Mapping
Read ~/.pathfinder/skill/SKILL.md at session start.
Commands: /map, /blaze, /scout, /summit
When invoked, read the matching skill from ~/.pathfinder/skill/references/{mapping,blazing,scouting,summiting}.md.
Scripts: ~/.pathfinder/skill/scripts/ and ~/.pathfinder/skill/scripts/
Run scripts with python3. All output JSON to stdout, errors to stderr.
'

echo "🔧 Setting up for Codex..."

TARGET="${PWD}/AGENTS.md"
if [ -f "$TARGET" ] && grep -q "Pathfinder" "$TARGET" 2>/dev/null; then
  echo "⚠️  Pathfinder already in AGENTS.md"
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
echo "🧭 Done! Tell Codex: /map"
