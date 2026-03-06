#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${PATHFINDER_HOME:-${HOME}/.agents/skills/pathfinder}"
LEGACY_HOME="${HOME}/.pathfinder"
REPO="https://github.com/srpadrono/Pathfinder.git"

echo "Pathfinder Installer"
echo ""

# Step 0: Migrate from legacy ~/.pathfinder if present
if [ -d "$LEGACY_HOME/.git" ] && [ "$PATHFINDER_HOME" != "$LEGACY_HOME" ]; then
  echo "Migrating from ~/.pathfinder to $PATHFINDER_HOME..."
  mkdir -p "$(dirname "$PATHFINDER_HOME")"
  mv "$LEGACY_HOME" "$PATHFINDER_HOME"
  echo "Migration complete."
fi

# Step 1: Install or update
if [ -d "$PATHFINDER_HOME/.git" ]; then
  echo "Updating..."
  git -C "$PATHFINDER_HOME" pull origin main --quiet
else
  if [ -d "$PATHFINDER_HOME" ]; then
    echo "Removing non-git directory at $PATHFINDER_HOME..."
    rm -rf "$PATHFINDER_HOME"
  fi
  mkdir -p "$(dirname "$PATHFINDER_HOME")"
  echo "Installing..."
  git clone --quiet "$REPO" "$PATHFINDER_HOME"
fi
echo "Installed at $PATHFINDER_HOME"

# Step 2: Register as Claude Code marketplace + install plugin
echo ""
if command -v claude &>/dev/null; then
  echo "Registering Pathfinder marketplace..."
  if claude plugin marketplace add srpadrono/Pathfinder --scope user 2>/dev/null; then
    echo "Marketplace registered."
    echo "Installing pathfinder plugin..."
    if claude plugin install pathfinder 2>/dev/null; then
      echo "Plugin installed."
    else
      echo "Plugin install failed — try: claude plugin install pathfinder"
    fi
  else
    echo "Marketplace registration failed — try: claude plugin marketplace add srpadrono/Pathfinder"
  fi
else
  echo "Claude Code CLI not found. To install the plugin later:"
  echo "  claude plugin marketplace add srpadrono/Pathfinder"
  echo "  claude plugin install pathfinder"
fi

# Step 3: Verify Python
echo ""
if python3 -c "import json" 2>/dev/null; then
  echo "Python 3 available"
else
  echo "Warning: Python 3 not found — install it with: brew install python"
fi

echo ""
echo "Done! Next steps:"
echo "  cd your-project"
echo "  python3 $PATHFINDER_HOME/skills/pathfinder/scripts/pathfinder-init.py"
echo "  Then use /map to start"
