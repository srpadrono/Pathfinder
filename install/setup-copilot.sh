#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"

echo "🔧 Setting up for GitHub Copilot CLI..."

# Create .github/instructions/ directory
mkdir -p "${PWD}/.github/instructions"

TARGET="${PWD}/.github/instructions/pathfinder.instructions.md"

if [ -f "$TARGET" ] && grep -q "Pathfinder" "$TARGET" 2>/dev/null; then
  echo "⚠️  Pathfinder instructions already exist at $TARGET"
else
  cat > "$TARGET" << 'INSTRUCTIONS'
---
applyTo: "**"
---

# Pathfinder — UI Test Coverage Mapping

Pathfinder is installed at ~/.pathfinder. It maps user journeys in a codebase, visualizes test coverage with Mermaid diagrams, and generates framework-correct UI tests.

## Commands

When the user says /map, /blaze, /scout, or /summit, read the matching skill file and follow its instructions:

- `/map` → Read `~/.pathfinder/skills/mapping/SKILL.md`
- `/blaze` → Read `~/.pathfinder/skills/blazing/SKILL.md`
- `/scout` → Read `~/.pathfinder/skills/scouting/SKILL.md`
- `/summit` → Read `~/.pathfinder/skills/summiting/SKILL.md`

Full overview: `~/.pathfinder/skills/using-pathfinder/SKILL.md`

## Scripts

All scripts are Python 3 CLIs. Run them with `python3`. They output JSON to stdout and errors to stderr.

```bash
python3 ~/.pathfinder/scripts/pathfinder-init.py                              # Initialize
python3 ~/.pathfinder/skills/mapping/scripts/scan-test-coverage.py .          # Scan tests
python3 ~/.pathfinder/skills/blazing/scripts/generate-diagrams.py .pathfinder/journeys.json  # Diagrams
python3 ~/.pathfinder/skills/ui-testing/scripts/detect-ui-framework.py .      # Detect framework
python3 ~/.pathfinder/skills/ui-testing/scripts/generate-ui-test.py ID "desc" framework --auto  # Generate test
python3 ~/.pathfinder/scripts/coverage-score.py .pathfinder/journeys.json     # Coverage score
```

## Project Files

- `.pathfinder/config.json` — project configuration (framework, test directory)
- `.pathfinder/journeys.json` — journey map (source of truth)
- `.pathfinder/blazes.md` — Mermaid coverage diagrams (auto-generated)

## Framework References

When writing tests, read the matching reference for correct selectors, waits, and patterns:
- `~/.pathfinder/skills/ui-testing/references/playwright.md`
- `~/.pathfinder/skills/ui-testing/references/cypress.md`
- `~/.pathfinder/skills/ui-testing/references/maestro.md`
- `~/.pathfinder/skills/ui-testing/references/detox.md`
- `~/.pathfinder/skills/ui-testing/references/xcuitest.md`
- `~/.pathfinder/skills/ui-testing/references/espresso.md`
- `~/.pathfinder/skills/ui-testing/references/flutter-test.md`
INSTRUCTIONS
  echo "✅ Created $TARGET"
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
echo "   Instructions at: .github/instructions/pathfinder.instructions.md"
