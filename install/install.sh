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

# Step 2: Detect platform
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
read -p "Select (1-8): " choice

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
