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

- `/map` → Read `~/.pathfinder/references/mapping.md`
- `/blaze` → Read `~/.pathfinder/references/blazing.md`
- `/scout` → Read `~/.pathfinder/references/scouting.md`
- `/summit` → Read `~/.pathfinder/references/summiting.md`

Full overview: `~/.pathfinder/SKILL.md`

## Scripts

All scripts are Python 3 CLIs. Run them with `python3`. They output JSON to stdout and errors to stderr.

```bash
python3 ~/.pathfinder/scripts/pathfinder-init.py                              # Initialize
python3 ~/.pathfinder/scripts/scan-test-coverage.py .          # Scan tests
python3 ~/.pathfinder/scripts/generate-diagrams.py .pathfinder/journeys.json  # Diagrams
python3 ~/.pathfinder/scripts/detect-ui-framework.py .      # Detect framework
python3 ~/.pathfinder/scripts/generate-ui-test.py ID "desc" framework --auto  # Generate test
python3 ~/.pathfinder/scripts/coverage-score.py .pathfinder/journeys.json     # Coverage score
```

## Project Files

- `.pathfinder/config.json` — project configuration (framework, test directory)
- `.pathfinder/journeys.json` — journey map (source of truth)
- `.pathfinder/blazes.md` — Mermaid coverage diagrams (auto-generated)

## Framework References

When writing tests, read the matching reference for correct selectors, waits, and patterns:
- `~/.pathfinder/references/playwright.md`
- `~/.pathfinder/references/cypress.md`
- `~/.pathfinder/references/maestro.md`
- `~/.pathfinder/references/detox.md`
- `~/.pathfinder/references/xcuitest.md`
- `~/.pathfinder/references/espresso.md`
- `~/.pathfinder/references/flutter-test.md`
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
