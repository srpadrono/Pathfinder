#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"

echo "🔧 Setting up for GitHub Copilot CLI..."
echo ""
echo "Choose setup method:"
echo "  1) AGENTS.md (recommended — works in any directory)"
echo "  2) .github/copilot-instructions.md (repo-wide)"
echo "  3) Both"
echo ""
read -p "Select (1-3): " method

AGENTS_SNIPPET='
## Pathfinder — UI Test Coverage Mapping

I have Pathfinder installed at ~/.pathfinder.

### Commands
When I say /map, /blaze, /scout, or /summit, read the matching skill and follow it:
- /map → Read ~/.pathfinder/skills/mapping/SKILL.md
- /blaze → Read ~/.pathfinder/skills/blazing/SKILL.md
- /scout → Read ~/.pathfinder/skills/scouting/SKILL.md
- /summit → Read ~/.pathfinder/skills/summiting/SKILL.md

### Overview
Read ~/.pathfinder/skills/using-pathfinder/SKILL.md for the full workflow.

### Scripts
All scripts are Python 3 CLIs at ~/.pathfinder/scripts/ and ~/.pathfinder/skills/*/scripts/.
They accept CLI arguments and output JSON to stdout, errors to stderr.
'

COPILOT_INSTRUCTIONS='## Pathfinder — UI Test Coverage Mapping

This project uses Pathfinder for UI test coverage mapping.
Pathfinder is installed at ~/.pathfinder.

When asked to /map, /blaze, /scout, or /summit:
1. Read the matching skill from ~/.pathfinder/skills/{mapping,blazing,scouting,summiting}/SKILL.md
2. Follow the instructions in that file
3. Use scripts from ~/.pathfinder/scripts/ and ~/.pathfinder/skills/*/scripts/

Journey data is stored in .pathfinder/journeys.json.
Coverage diagrams are in .pathfinder/blazes.md.
Project config is in .pathfinder/config.json.
'

if [ "$method" = "1" ] || [ "$method" = "3" ]; then
  TARGET="${PWD}/AGENTS.md"
  if [ -f "$TARGET" ] && grep -q "Pathfinder" "$TARGET" 2>/dev/null; then
    echo "⚠️  Pathfinder already in AGENTS.md"
  else
    echo "$AGENTS_SNIPPET" >> "$TARGET"
    echo "✅ Added to $TARGET"
  fi
fi

if [ "$method" = "2" ] || [ "$method" = "3" ]; then
  mkdir -p "${PWD}/.github"
  TARGET="${PWD}/.github/copilot-instructions.md"
  if [ -f "$TARGET" ] && grep -q "Pathfinder" "$TARGET" 2>/dev/null; then
    echo "⚠️  Pathfinder already in copilot-instructions.md"
  else
    echo "$COPILOT_INSTRUCTIONS" >> "$TARGET"
    echo "✅ Added to $TARGET"
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
echo "🧭 Done! Tell Copilot: /map"
