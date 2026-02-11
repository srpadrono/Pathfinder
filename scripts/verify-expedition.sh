#!/usr/bin/env bash
# Pathfinder Pre-PR Verification Script
# Run this before creating a PR to verify all gates and evidence.
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

echo "🔍 Pathfinder Expedition Verification"
echo "======================================"
echo ""

# 1. Check gate files
echo "📋 Phase 1: Gate Files"
for gate in survey plan scout build; do
  file=".pathfinder/${gate}.json"
  if [ ! -f "$file" ]; then
    echo -e "  ${RED}✘ Missing: $file${NC}"
    ERRORS=$((ERRORS + 1))
  else
    status=$(python3 -c "import json; print(json.load(open('$file')).get('status','missing'))" 2>/dev/null || echo "parse-error")
    if [ "$status" = "approved" ] || [ "$status" = "complete" ]; then
      echo -e "  ${GREEN}✓ $file (status: $status)${NC}"
    else
      echo -e "  ${RED}✘ $file has status: $status (expected approved/complete)${NC}"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done
echo ""

# 2. Check evidence blocks
echo "📋 Phase 2: Evidence Blocks"
if [ -f ".pathfinder/plan.json" ]; then
  checkpoints=$(python3 -c "
import json
plan = json.load(open('.pathfinder/plan.json'))
cps = plan.get('checkpoints', [])
for cp in cps:
    if isinstance(cp, dict):
        print(cp.get('id', ''))
    else:
        print(cp)
" 2>/dev/null)

  for cp in $checkpoints; do
    if [ -z "$cp" ]; then continue; fi
    # Search for evidence block in any .md file or build log
    found=$(grep -r "EVIDENCE:${cp}" . --include="*.md" 2>/dev/null | head -1 || true)
    if [ -n "$found" ]; then
      echo -e "  ${GREEN}✓ Evidence found for $cp${NC}"
    else
      echo -e "  ${YELLOW}⚠ No evidence block for $cp${NC}"
      ERRORS=$((ERRORS + 1))
    fi
  done
else
  echo -e "  ${RED}✘ Cannot check evidence — .pathfinder/plan.json missing${NC}"
  ERRORS=$((ERRORS + 1))
fi
echo ""

# 3. Check USER-JOURNEYS.md markers
echo "📋 Phase 3: Trail Map Markers"
if [ -f "USER-JOURNEYS.md" ]; then
  remaining=$(grep -c "❌\|🔄" USER-JOURNEYS.md 2>/dev/null || echo "0")
  cleared=$(grep -c "✅" USER-JOURNEYS.md 2>/dev/null || echo "0")
  echo "  Cleared: $cleared | Remaining: $remaining"
  if [ "$remaining" -gt 0 ]; then
    echo -e "  ${YELLOW}⚠ $remaining checkpoints not marked as cleared${NC}"
  else
    echo -e "  ${GREEN}✓ All markers show ✅${NC}"
  fi
else
  echo -e "  ${YELLOW}⚠ USER-JOURNEYS.md not found${NC}"
fi
echo ""

# 4. Check for secrets
echo "📋 Phase 4: Security Check"
secrets_found=$(git diff --name-only main..HEAD 2>/dev/null | grep -E "\.env$|\.env\.local$|\.env\.production$|secrets|credentials" || true)
if [ -n "$secrets_found" ]; then
  echo -e "  ${RED}✘ Potential secrets in diff:${NC}"
  echo "$secrets_found" | while read -r f; do echo "    - $f"; done
  ERRORS=$((ERRORS + 1))
else
  echo -e "  ${GREEN}✓ No secret files in diff${NC}"
fi
echo ""

# 5. Summary
echo "======================================"
if [ "$ERRORS" -gt 0 ]; then
  echo -e "${RED}✘ $ERRORS issue(s) found. Fix before creating PR.${NC}"
  exit 1
else
  echo -e "${GREEN}✓ All checks passed. Ready for PR.${NC}"
  exit 0
fi
