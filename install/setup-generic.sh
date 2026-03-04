#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"

echo "🔧 Generic setup"
echo ""
echo "Add this to your agent's instruction file (CLAUDE.md, AGENTS.md, .cursorrules, etc.):"
echo ""
echo "---"
cat << 'SNIPPET'
## Pathfinder — UI Test Coverage Mapping

I have Pathfinder installed at ~/.pathfinder. It maps user journeys and generates UI tests.

Commands:
- /map — Read ~/.pathfinder/skills/mapping/SKILL.md and follow it
- /blaze — Read ~/.pathfinder/skills/blazing/SKILL.md and follow it
- /scout — Read ~/.pathfinder/skills/scouting/SKILL.md and follow it
- /summit — Read ~/.pathfinder/skills/summiting/SKILL.md and follow it

Scripts are CLI tools (python3). All output JSON to stdout, errors to stderr.
SNIPPET
echo "---"
echo ""

read -p "Enable git hooks in current project? (y/n): " hooks
if [ "$hooks" = "y" ]; then
  git config core.hooksPath "$PATHFINDER_HOME/.githooks"
  echo "✅ Git hooks enabled"
fi

echo ""
echo "🧭 Copy the snippet above into your agent config."
