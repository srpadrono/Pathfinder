#!/usr/bin/env bash
set -euo pipefail

REPO="https://github.com/srpadrono/Pathfinder.git"
REPO_HOME="${HOME}/.agents/pathfinder"
SKILLS_HOME="${HOME}/.agents/skills"
LEGACY_HOME="${HOME}/.pathfinder"

info()  { echo "  $*"; }
error() { echo "ERROR: $*" >&2; }

echo "Pathfinder Installer"
echo ""

# Prerequisites
for cmd in git python3; do
  if ! command -v "$cmd" &>/dev/null; then
    error "$cmd is required but not found."
    [ "$cmd" = "python3" ] && info "Install with: brew install python (macOS) or sudo apt install python3"
    [ "$cmd" = "git" ] && info "Install with: brew install git (macOS) or sudo apt install git"
    exit 1
  fi
done

# Step 1: Migrate from legacy ~/.pathfinder if present
if [ -d "$LEGACY_HOME/.git" ]; then
  echo "Migrating from $LEGACY_HOME to $REPO_HOME..."
  mkdir -p "$(dirname "$REPO_HOME")"
  mv "$LEGACY_HOME" "$REPO_HOME"
  info "Migration complete."
  echo ""
fi

# Step 2: Clone or update
if [ -d "$REPO_HOME/.git" ]; then
  echo "Updating $REPO_HOME..."
  git -C "$REPO_HOME" pull origin main --quiet
else
  mkdir -p "$(dirname "$REPO_HOME")"
  echo "Cloning to $REPO_HOME..."
  git clone --quiet "$REPO" "$REPO_HOME"
fi

# Step 3: Symlink skills into ~/.agents/skills/
mkdir -p "$SKILLS_HOME"
for skill_dir in "$REPO_HOME"/skills/*/; do
  skill_name=$(basename "$skill_dir")
  link="$SKILLS_HOME/$skill_name"
  if [ -L "$link" ]; then
    rm "$link"
  elif [ -e "$link" ]; then
    info "Skipping $link (already exists and is not a symlink)"
    continue
  fi
  ln -s "$skill_dir" "$link"
done
echo "Skills linked into $SKILLS_HOME/"

# Step 4: Register as Claude Code plugin (optional)
echo ""
if command -v claude &>/dev/null; then
  echo "Registering Pathfinder plugin..."
  if claude plugin marketplace add srpadrono/Pathfinder --scope user 2>/dev/null; then
    if claude plugin install pathfinder 2>/dev/null; then
      info "Plugin installed."
    else
      info "Plugin install failed — try: claude plugin install pathfinder"
    fi
  else
    info "Marketplace registration failed — try: claude plugin marketplace add srpadrono/Pathfinder"
  fi
else
  echo "Claude Code CLI not found. To install the plugin later:"
  info "claude plugin marketplace add srpadrono/Pathfinder"
  info "claude plugin install pathfinder"
fi

echo ""
echo "Done! Installed:"
info "Repo:   $REPO_HOME"
info "Skills: $SKILLS_HOME/pathfinder -> $REPO_HOME/skills/pathfinder"
echo ""
echo "Next steps:"
info "cd your-project"
info "python3 ~/.agents/skills/pathfinder/scripts/pathfinder-init.py"
info "Then use /map to start"
