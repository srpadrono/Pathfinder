#!/usr/bin/env bash
set -euo pipefail

if [ ! -f "eslint.config.js" ] && [ ! -f "eslint.config.mjs" ] && [ ! -f "eslint.config.cjs" ]; then
  echo "⚠ ESLint config not found (eslint.config.*). Skipping lint."
  echo "  Add eslint.config.js to enable lint enforcement."
  exit 0
fi

paths=("scripts/" "e2e/")
if [ -d "src" ]; then
  paths+=("src/")
fi

npx eslint "${paths[@]}"
