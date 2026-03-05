#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"

echo "🔧 Setting up Pathfinder for GitHub Copilot CLI..."
echo ""
echo "Choose setup method:"
echo "  1) Environment variable (recommended — works across ALL repos, no files copied)"
echo "  2) Per-repo .github/instructions/ file"
echo "  3) Global ~/.copilot/copilot-instructions.md"
echo ""
read -p "Select (1-3): " method

case "$method" in
  1)
    # COPILOT_CUSTOM_INSTRUCTIONS_DIRS — Copilot reads AGENTS.md and
    # .github/instructions/*.instructions.md from these directories.
    # We create a minimal AGENTS.md in the skill dir.

    AGENTS_FILE="$PATHFINDER_HOME/skill/AGENTS.md"
    if [ ! -f "$AGENTS_FILE" ]; then
      cat > "$AGENTS_FILE" << 'AGENTSEOF'
# Pathfinder

Read SKILL.md in this directory for full instructions.

When the user says /map, /blaze, /scout, or /summit, read the matching reference file and follow it:
- /map → references/mapping.md
- /blaze → references/blazing.md
- /scout → references/scouting.md
- /summit → references/summiting.md

Scripts are in scripts/. All Python 3 CLIs outputting JSON to stdout.
AGENTSEOF
      echo "✅ Created $AGENTS_FILE"
    fi

    echo ""
    echo "Add this to your shell profile (~/.zshrc or ~/.bashrc):"
    echo ""
    echo "  export COPILOT_CUSTOM_INSTRUCTIONS_DIRS=\"$PATHFINDER_HOME/skill\""
    echo ""

    # Offer to add automatically
    SHELL_RC=""
    if [ -f "$HOME/.zshrc" ]; then
      SHELL_RC="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
      SHELL_RC="$HOME/.bashrc"
    fi

    if [ -n "$SHELL_RC" ]; then
      read -p "Add to $SHELL_RC automatically? (y/n): " auto
      if [ "$auto" = "y" ]; then
        if grep -q "COPILOT_CUSTOM_INSTRUCTIONS_DIRS" "$SHELL_RC" 2>/dev/null; then
          echo "⚠️  COPILOT_CUSTOM_INSTRUCTIONS_DIRS already in $SHELL_RC — check it includes $PATHFINDER_HOME/skill"
        else
          echo "" >> "$SHELL_RC"
          echo "# Pathfinder for GitHub Copilot CLI" >> "$SHELL_RC"
          echo "export COPILOT_CUSTOM_INSTRUCTIONS_DIRS=\"$PATHFINDER_HOME/skill\"" >> "$SHELL_RC"
          echo "✅ Added to $SHELL_RC"
          echo "   Run: source $SHELL_RC"
        fi
      fi
    fi
    ;;

  2)
    # Per-repo .github/instructions/ file
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

Pathfinder is installed at ~/.pathfinder/skill. It maps user journeys, visualizes test coverage with Mermaid flowcharts, and generates framework-correct UI tests.

## Commands

When the user says /map, /blaze, /scout, or /summit, read the matching file and follow it:

- `/map` → Read `~/.pathfinder/skill/references/mapping.md`
- `/blaze` → Read `~/.pathfinder/skill/references/blazing.md`
- `/scout` → Read `~/.pathfinder/skill/references/scouting.md`
- `/summit` → Read `~/.pathfinder/skill/references/summiting.md`

Full overview: `~/.pathfinder/skill/SKILL.md`

## Scripts

All Python 3 CLIs at `~/.pathfinder/skill/scripts/`. Output JSON to stdout, errors to stderr.

- `pathfinder-init.py` — Initialize Pathfinder in a project
- `scan-test-coverage.py .` — Scan existing tests
- `detect-ui-framework.py .` — Auto-detect UI framework
- `generate-diagrams.py .pathfinder/journeys.json` — Generate flowcharts
- `generate-ui-test.py ID "desc" framework --auto` — Generate/append test
- `coverage-score.py .pathfinder/journeys.json` — Coverage score

## Project Files

- `.pathfinder/config.json` — project config
- `.pathfinder/journeys.json` — journey map (source of truth)
- `.pathfinder/blazes.md` — Mermaid flowcharts (auto-generated)

## Framework References

Read the matching reference at `~/.pathfinder/skill/references/` for correct selectors, waits, and patterns: playwright.md, cypress.md, maestro.md, detox.md, xcuitest.md, espresso.md, flutter-test.md
INSTRUCTIONS
      echo "✅ Created $TARGET"
    fi
    ;;

  3)
    # Global ~/.copilot/copilot-instructions.md
    mkdir -p "$HOME/.copilot"
    TARGET="$HOME/.copilot/copilot-instructions.md"

    if [ -f "$TARGET" ] && grep -q "Pathfinder" "$TARGET" 2>/dev/null; then
      echo "⚠️  Pathfinder already in $TARGET"
    else
      cat >> "$TARGET" << 'GLOBALEOF'

## Pathfinder — UI Test Coverage Mapping

Pathfinder is installed at ~/.pathfinder/skill. When the user says /map, /blaze, /scout, or /summit:
1. Read ~/.pathfinder/skill/SKILL.md for the full overview
2. Read the matching reference: ~/.pathfinder/skill/references/{mapping,blazing,scouting,summiting}.md
3. Use scripts at ~/.pathfinder/skill/scripts/ (Python 3 CLIs, JSON output)
GLOBALEOF
      echo "✅ Appended to $TARGET"
    fi
    ;;

  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

# Git hooks
echo ""
read -p "Enable Pathfinder git hooks in current project? (y/n): " hooks
if [ "$hooks" = "y" ]; then
  git config core.hooksPath "$PATHFINDER_HOME/.githooks"
  echo "✅ Git hooks enabled"
fi

echo ""
echo "🧭 Done! Tell Copilot: /map"
