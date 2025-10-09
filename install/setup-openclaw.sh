#!/usr/bin/env bash
set -euo pipefail

PATHFINDER_HOME="${HOME}/.pathfinder"

echo "🔧 Setting up for OpenClaw..."

# Find OpenClaw skills directory
OPENCLAW_SKILLS=""
for candidate in \
  "${HOME}/.npm-global/lib/node_modules/openclaw/skills" \
  "/usr/local/lib/node_modules/openclaw/skills" \
  "/usr/lib/node_modules/openclaw/skills"; do
  if [ -d "$candidate" ]; then
    OPENCLAW_SKILLS="$candidate"
    break
  fi
done

if [ -z "$OPENCLAW_SKILLS" ]; then
  echo "❌ OpenClaw skills directory not found."
  echo "   Manually symlink: ln -s $PATHFINDER_HOME <openclaw-skills-dir>/pathfinder"
  exit 1
fi

LINK="$OPENCLAW_SKILLS/pathfinder"
if [ -L "$LINK" ] || [ -d "$LINK" ]; then
  echo "⚠️  Pathfinder already linked at $LINK"
else
  ln -s "$PATHFINDER_HOME" "$LINK"
  echo "✅ Symlinked to $LINK"
fi

read -p "Enable git hooks in current project? (y/n): " hooks
if [ "$hooks" = "y" ]; then
  git config core.hooksPath "$PATHFINDER_HOME/.githooks"
  echo "✅ Git hooks enabled"
fi

echo ""
echo "🧭 Done! Pathfinder skills auto-load via session-start hook."
