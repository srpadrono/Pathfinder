#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"
REPO="https://github.com/srpadrono/Pathfinder.git"

echo "🧭 Pathfinder Installer"
echo ""

# Step 1: Clone or update
if [ -d "$PATHFINDER_HOME" ]; then
  echo "📦 Updating existing installation..."
  cd "$PATHFINDER_HOME" && git pull origin main --quiet
else
  echo "📦 Cloning Pathfinder..."
  git clone --quiet "$REPO" "$PATHFINDER_HOME"
fi

echo "✅ Installed at $PATHFINDER_HOME"
echo ""

# Parse --platform flag for non-interactive use
PLATFORM=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --platform)
      PLATFORM="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Map platform name to choice number
platform_to_choice() {
  case "$1" in
    claude|claude-code) echo 1 ;;
    copilot|github-copilot) echo 2 ;;
    codex) echo 3 ;;
    openclaw) echo 4 ;;
    cursor) echo 5 ;;
    windsurf|codeium) echo 6 ;;
    aider) echo 7 ;;
    generic|other|manual) echo 8 ;;
    *) echo "" ;;
  esac
}

# Step 2: Determine platform
if [ -n "$PLATFORM" ]; then
  # Non-interactive: use --platform flag
  choice=$(platform_to_choice "$PLATFORM")
  if [ -z "$choice" ]; then
    echo "❌ Unknown platform: $PLATFORM"
    echo "   Valid: claude-code, copilot, codex, openclaw, cursor, windsurf, aider, generic"
    exit 1
  fi
  echo "🔧 Setting up for: $PLATFORM"
else
  # Auto-detect platform from project files
  detected=""
  if [ -f "CLAUDE.md" ]; then
    detected="Claude Code"
    default_choice=1
  elif [ -d ".github/instructions" ]; then
    detected="GitHub Copilot"
    default_choice=2
  elif [ -f "AGENTS.md" ]; then
    detected="Codex"
    default_choice=3
  elif [ -f ".cursorrules" ]; then
    detected="Cursor"
    default_choice=5
  elif [ -f ".windsurfrules" ]; then
    detected="Windsurf"
    default_choice=6
  elif [ -f ".aider.conf.yml" ]; then
    detected="Aider"
    default_choice=7
  fi

  echo "Which platform are you using?"
  echo ""
  echo "  1) Claude Code"
  echo "  2) GitHub Copilot CLI"
  echo "  3) Codex (OpenAI)"
  echo "  4) OpenClaw"
  echo "  5) Cursor"
  echo "  6) Windsurf / Codeium"
  echo "  7) Aider"
  echo "  8) Other / Manual"
  echo ""

  if [ -n "$detected" ]; then
    read -p "Detected: $detected. Press Enter to confirm, or select (1-8): " choice
    choice="${choice:-$default_choice}"
  else
    read -p "Select (1-8): " choice
  fi
fi

case $choice in
  1) bash "$PATHFINDER_HOME/install/setup-claude-code.sh" ;;
  2) bash "$PATHFINDER_HOME/install/setup-copilot.sh" ;;
  3) bash "$PATHFINDER_HOME/install/setup-codex.sh" ;;
  4) bash "$PATHFINDER_HOME/install/setup-openclaw.sh" ;;
  5) bash "$PATHFINDER_HOME/install/setup-cursor.sh" ;;
  6) bash "$PATHFINDER_HOME/install/setup-windsurf.sh" ;;
  7) bash "$PATHFINDER_HOME/install/setup-aider.sh" ;;
  8) bash "$PATHFINDER_HOME/install/setup-generic.sh" ;;
  *) echo "Invalid choice"; exit 1 ;;
esac

# Step 3: Verify
echo ""
echo "🔍 Verifying installation..."
if python3 -c "import json" 2>/dev/null; then
  echo "✅ Python 3 available"
else
  echo "⚠️  Python 3 not found — install it to use Pathfinder scripts"
fi
if [ -f "$PATHFINDER_HOME/skill/SKILL.md" ] && [ -f "$PATHFINDER_HOME/skill/scripts/pathfinder-init.py" ]; then
  echo "✅ All skill files present"
else
  echo "⚠️  Some files missing — try: cd ~/.pathfinder && git pull origin main"
fi

echo ""
echo "📋 Next steps:"
echo "   cd your-project"
echo "   python3 ~/.pathfinder/skill/scripts/pathfinder-init.py"
echo "   Then tell your agent: /map"
