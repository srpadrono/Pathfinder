#!/usr/bin/env bash
set -euo pipefail

# ─── Pathfinder Installer ───────────────────────────────────────────────
# https://github.com/srpadrono/Pathfinder
#
# Usage:
#   bash <(curl -fsSL .../install.sh)                   # install
#   bash <(curl -fsSL .../install.sh) update             # update
#   bash <(curl -fsSL .../install.sh) uninstall          # uninstall
#   bash <(curl -fsSL .../install.sh) --version v2.1.0   # pin version
#   bash <(curl -fsSL .../install.sh) --help             # help
# ─────────────────────────────────────────────────────────────────────────

VERSION="2.1.0"
REPO="https://github.com/srpadrono/Pathfinder.git"
REPO_HOME="${HOME}/.agents/pathfinder"
SKILLS_HOME="${HOME}/.agents/skills"
LEGACY_HOME="${HOME}/.pathfinder"

# ─── Colors ──────────────────────────────────────────────────────────────

if [ -t 1 ]; then
  GREEN="$(tput setaf 2 2>/dev/null || printf '')"
  RED="$(tput setaf 1 2>/dev/null || printf '')"
  YELLOW="$(tput setaf 3 2>/dev/null || printf '')"
  BLUE="$(tput setaf 4 2>/dev/null || printf '')"
  BOLD="$(tput bold 2>/dev/null || printf '')"
  RESET="$(tput sgr0 2>/dev/null || printf '')"
else
  GREEN="" RED="" YELLOW="" BLUE="" BOLD="" RESET=""
fi

info()      { printf '%s\n' "${BOLD}${BLUE}>${RESET} $*"; }
success()   { printf '%s\n' "${GREEN}✓${RESET} $*"; }
warn()      { printf '%s\n' "${YELLOW}!${RESET} $*"; }
error()     { printf '%s\n' "${RED}✗${RESET} $*" >&2; }

# ─── Cleanup trap ────────────────────────────────────────────────────────

CLEANUP_ACTION=""

cleanup() {
  local exit_code=$?
  if [ $exit_code -ne 0 ] && [ -n "$CLEANUP_ACTION" ]; then
    echo ""
    error "Installation failed."
    case "$CLEANUP_ACTION" in
      fresh_install)
        warn "Cleaning up partial install..."
        rm -rf "$REPO_HOME"
        remove_symlinks 2>/dev/null || true
        ;;
      migration)
        warn "Restoring previous install..."
        if [ -d "$REPO_HOME" ] && [ ! -d "$LEGACY_HOME" ]; then
          mv "$REPO_HOME" "$LEGACY_HOME"
        fi
        ;;
      # update: leave existing install intact — git pull is atomic
    esac
  fi
  return $exit_code
}

trap cleanup EXIT

# ─── Helpers ─────────────────────────────────────────────────────────────

check_prereqs() {
  local missing=0
  for cmd in git python3; do
    if ! command -v "$cmd" &>/dev/null; then
      error "$cmd is required but not found."
      case "$cmd" in
        python3) warn "  Install with: brew install python (macOS) or sudo apt install python3" ;;
        git)     warn "  Install with: brew install git (macOS) or sudo apt install git" ;;
      esac
      missing=1
    fi
  done
  [ $missing -eq 0 ] || exit 1
}

create_symlinks() {
  mkdir -p "$SKILLS_HOME"
  for skill_dir in "$REPO_HOME"/skills/*/; do
    [ -d "$skill_dir" ] || continue
    local skill_name
    skill_name=$(basename "$skill_dir")
    local link="$SKILLS_HOME/$skill_name"
    if [ -L "$link" ]; then
      rm "$link"
    elif [ -e "$link" ]; then
      warn "Skipping $link (exists and is not a symlink)"
      continue
    fi
    ln -s "$skill_dir" "$link"
  done
}

remove_symlinks() {
  for skill_dir in "$REPO_HOME"/skills/*/; do
    [ -d "$skill_dir" ] || continue
    local skill_name
    skill_name=$(basename "$skill_dir")
    local link="$SKILLS_HOME/$skill_name"
    if [ -L "$link" ]; then
      rm "$link"
    fi
  done
}

register_plugin() {
  if command -v claude &>/dev/null; then
    info "Registering Claude Code plugin..."
    local mp_err plugin_err
    if mp_err=$(claude plugin marketplace add srpadrono/Pathfinder --scope user 2>&1); then
      if plugin_err=$(claude plugin install pathfinder 2>&1); then
        success "Claude Code plugin installed."
      else
        warn "Plugin install failed: $plugin_err"
        warn "  Try manually: claude plugin install pathfinder"
      fi
    else
      warn "Marketplace registration failed: $mp_err"
      warn "  Try manually: claude plugin marketplace add srpadrono/Pathfinder --scope user"
    fi
  else
    info "Claude Code CLI not found — plugin registration skipped."
    info "  Install later: claude plugin marketplace add srpadrono/Pathfinder --scope user"
    info "                 claude plugin install pathfinder"
  fi
}

unregister_plugin() {
  if command -v claude &>/dev/null; then
    info "Removing Claude Code plugin..."
    claude plugin uninstall pathfinder 2>/dev/null && success "Plugin removed." || true
    claude plugin marketplace remove pathfinder 2>/dev/null || true
  fi
}

PATHFINDER_SNIPPET='## Pathfinder — UI Test Coverage Mapping

Pathfinder is installed at ~/.agents/skills/pathfinder. It maps user journeys,
visualizes test coverage with Mermaid flowcharts, and generates framework-correct UI tests.

Commands: /map, /blaze, /scout, /summit — each is a skill that activates automatically.

Full overview: ~/.agents/skills/pathfinder/SKILL.md
Scripts: ~/.agents/skills/pathfinder/scripts/ (Python 3 CLIs, JSON output)'

inject_agent_instructions() {
  local files=(
    "${HOME}/.claude/CLAUDE.md"
    "${HOME}/.codex/AGENTS.md"
  )
  for file in "${files[@]}"; do
    [ -d "$(dirname "$file")" ] || continue
    if [ -f "$file" ] && grep -q "Pathfinder — UI Test Coverage Mapping" "$file" 2>/dev/null; then
      continue  # already present
    fi
    printf '\n\n%s\n' "$PATHFINDER_SNIPPET" >> "$file"
    success "Added Pathfinder snippet to $file"
  done
}

remove_agent_instructions() {
  local files=(
    "${HOME}/.claude/CLAUDE.md"
    "${HOME}/.codex/AGENTS.md"
  )
  for file in "${files[@]}"; do
    [ -f "$file" ] || continue
    if grep -q "Pathfinder — UI Test Coverage Mapping" "$file" 2>/dev/null; then
      # Remove the snippet block (from ## Pathfinder header to Scripts: line)
      sed -i.bak '/## Pathfinder — UI Test Coverage Mapping/,/Scripts:.*JSON output)/d' "$file"
      # Clean up trailing blank lines left behind
      sed -i.bak -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$file"
      rm -f "${file}.bak"
      success "Removed Pathfinder snippet from $file"
    fi
  done
}

checkout_version() {
  local version="$1"
  if ! git -C "$REPO_HOME" rev-parse "$version" &>/dev/null; then
    error "Version $version not found. Available tags:"
    git -C "$REPO_HOME" tag -l | sed 's/^/  /'
    exit 1
  fi
  git -C "$REPO_HOME" checkout --quiet "$version"
  success "Pinned to $version"
}

# ─── Commands ────────────────────────────────────────────────────────────

cmd_install() {
  local pin_version=""

  while [ $# -gt 0 ]; do
    case "$1" in
      --version) pin_version="${2:-}"; [ -n "$pin_version" ] || { error "--version requires a value"; exit 1; }; shift 2 ;;
      *) error "Unknown option: $1"; cmd_help; exit 1 ;;
    esac
  done

  check_prereqs

  echo ""
  printf '%s\n' "${BOLD}Pathfinder Installer${RESET}  v${VERSION}"
  echo ""

  # Migrate from legacy ~/.pathfinder
  if [ -d "$LEGACY_HOME/.git" ]; then
    CLEANUP_ACTION="migration"
    info "Migrating from $LEGACY_HOME to $REPO_HOME..."
    mkdir -p "$(dirname "$REPO_HOME")"
    mv "$LEGACY_HOME" "$REPO_HOME"
    success "Migration complete."
    echo ""
  fi

  # Clone or update
  if [ -d "$REPO_HOME/.git" ]; then
    info "Updating $REPO_HOME..."
    git -C "$REPO_HOME" fetch origin --quiet
    git -C "$REPO_HOME" reset --hard origin/main --quiet
    success "Updated to latest."
  else
    CLEANUP_ACTION="fresh_install"
    mkdir -p "$(dirname "$REPO_HOME")"
    info "Cloning to $REPO_HOME..."
    git clone --quiet "$REPO" "$REPO_HOME"
    success "Cloned."
  fi

  # Pin version if requested
  if [ -n "$pin_version" ]; then
    checkout_version "$pin_version"
  fi

  # Symlink skills
  create_symlinks
  success "Skills linked into $SKILLS_HOME/"

  # Register plugin
  echo ""
  register_plugin

  # Inject agent instructions into global config files
  echo ""
  inject_agent_instructions

  # Done
  CLEANUP_ACTION=""
  echo ""
  printf '%s\n' "${BOLD}${GREEN}Done!${RESET}"
  echo ""
  info "Repo:   $REPO_HOME"
  info "Skills: $SKILLS_HOME/pathfinder -> $REPO_HOME/skills/pathfinder"
  echo ""
  info "Next: cd your-project && use /map to start"
}

cmd_update() {
  local pin_version=""

  while [ $# -gt 0 ]; do
    case "$1" in
      --version) pin_version="${2:-}"; [ -n "$pin_version" ] || { error "--version requires a value"; exit 1; }; shift 2 ;;
      *) error "Unknown option: $1"; cmd_help; exit 1 ;;
    esac
  done

  if [ ! -d "$REPO_HOME/.git" ]; then
    error "Pathfinder is not installed at $REPO_HOME"
    info "Run the installer without arguments to install."
    exit 1
  fi

  check_prereqs

  echo ""
  printf '%s\n' "${BOLD}Pathfinder Update${RESET}"
  echo ""

  info "Pulling latest..."
  git -C "$REPO_HOME" fetch origin --tags --quiet

  # Validate version tag exists before changing anything
  if [ -n "$pin_version" ]; then
    if ! git -C "$REPO_HOME" rev-parse "$pin_version" &>/dev/null; then
      error "Version $pin_version not found. Available tags:"
      git -C "$REPO_HOME" tag -l | sed 's/^/  /'
      exit 1
    fi
  fi

  if [ -n "$pin_version" ]; then
    git -C "$REPO_HOME" checkout --quiet "$pin_version"
    success "Pinned to $pin_version"
  else
    git -C "$REPO_HOME" reset --hard origin/main --quiet
    success "Updated to latest."
  fi

  create_symlinks
  success "Skills refreshed."

  echo ""
  printf '%s\n' "${BOLD}${GREEN}Done!${RESET}"
}

cmd_uninstall() {
  echo ""
  printf '%s\n' "${BOLD}Pathfinder Uninstaller${RESET}"
  echo ""

  if [ ! -d "$REPO_HOME" ] && [ ! -L "$SKILLS_HOME/pathfinder" ]; then
    warn "Pathfinder is not installed."
    exit 0
  fi

  # Remove agent instructions
  remove_agent_instructions

  # Remove plugin
  unregister_plugin

  # Remove symlinks (works even if repo was manually deleted)
  if [ -d "$REPO_HOME" ]; then
    remove_symlinks
  else
    # Repo missing — clean up by known skill names
    for name in pathfinder map blaze scout summit; do
      local link="$SKILLS_HOME/$name"
      if [ -L "$link" ]; then
        rm "$link"
      fi
    done
  fi
  success "Symlinks removed."

  # Remove repo
  if [ -d "$REPO_HOME" ]; then
    rm -rf "$REPO_HOME"
    success "Removed $REPO_HOME"
  fi

  # Remove git hooks if pointing to pathfinder
  local hooks_path
  hooks_path=$(git config --global core.hooksPath 2>/dev/null || true)
  if [ "$hooks_path" = "$REPO_HOME/.githooks" ]; then
    git config --global --unset core.hooksPath
    success "Git hooks config cleaned."
  fi

  echo ""
  printf '%s\n' "${BOLD}${GREEN}Uninstalled.${RESET}"
}

cmd_help() {
  cat <<EOF

${BOLD}Pathfinder Installer${RESET}  v${VERSION}

${BOLD}USAGE${RESET}
  bash <(curl -fsSL https://raw.githubusercontent.com/srpadrono/Pathfinder/main/install/install.sh) [command] [options]

${BOLD}COMMANDS${RESET}
  install     Install Pathfinder (default)
  update      Pull latest and refresh symlinks
  uninstall   Remove Pathfinder completely

${BOLD}OPTIONS${RESET}
  --version <tag>   Pin to a specific version (e.g., v2.1.0)
  --help            Show this help

${BOLD}EXAMPLES${RESET}
  # Install latest
  bash <(curl -fsSL .../install.sh)

  # Install specific version
  bash <(curl -fsSL .../install.sh) --version v2.1.0

  # Update to latest
  bash <(curl -fsSL .../install.sh) update

  # Uninstall
  bash <(curl -fsSL .../install.sh) uninstall

${BOLD}PATHS${RESET}
  Repo:   ~/.agents/pathfinder
  Skills: ~/.agents/skills/pathfinder -> ~/.agents/pathfinder/skills/pathfinder

EOF
}

# ─── Main ────────────────────────────────────────────────────────────────

main() {
  local command="install"

  if [ $# -gt 0 ]; then
    case "$1" in
      install|update|uninstall) command="$1"; shift ;;
      --help|-h) cmd_help; exit 0 ;;
      --version) command="install" ;;  # pass through to cmd_install
      -*) command="install" ;;  # flags go to install by default
      *) error "Unknown command: $1"; cmd_help; exit 1 ;;
    esac
  fi

  "cmd_$command" "$@"
}

main "$@"
