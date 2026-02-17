#!/usr/bin/env bash
# Pathfinder v0.4.0 Expedition Verification
# Computes a quality score (0-100) and generates report.json.
set -euo pipefail

if ! command -v python3 &>/dev/null; then
  echo "✘ python3 is required but not found in PATH"
  exit 1
fi

SCORE=0
MAX_SCORE=100
ERRORS=0
TEST_OUTPUT=$(mktemp)
trap 'rm -f "$TEST_OUTPUT"' EXIT

resolve_default_branch() {
  local branch
  branch=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||' || true)
  if [ -n "$branch" ]; then
    echo "$branch"
    return
  fi

  for candidate in main master trunk develop; do
    if git show-ref --verify --quiet "refs/heads/$candidate" || git show-ref --verify --quiet "refs/remotes/origin/$candidate"; then
      echo "$candidate"
      return
    fi
  done

  echo ""
}

read_state_field() {
  local field="$1"
  local fallback="$2"
  python3 - << PY
import json
from pathlib import Path
state=Path('.pathfinder/state.json')
if not state.exists():
    print(${fallback@Q})
else:
    data=json.loads(state.read_text())
    print(data.get(${field@Q}, ${fallback@Q}))
PY
}

echo "🔍 Pathfinder Expedition Verification (v0.4.0)"
echo "================================================"

# --- Check state.json exists ---
if [ ! -f .pathfinder/state.json ]; then
  echo "⚠ Missing .pathfinder/state.json"
  echo "  This repo is not currently initialized as a Pathfinder expedition."
  echo "  To initialize, create:"
  echo "    - .pathfinder/state.json"
  echo "    - .pathfinder/{survey,plan,scout,build}.json"
  echo "    - .pathfinder/tasks/*.json"
  echo "  Then re-run: bash scripts/verify-expedition.sh"
  exit 2
fi

BRANCH=$(read_state_field 'branch' "$(git branch --show-current)")
EXPEDITION=$(read_state_field 'expedition' 'unknown')
BASE_BRANCH=$(resolve_default_branch)

echo "Expedition: $EXPEDITION | Branch: $BRANCH"
if [ -n "$BASE_BRANCH" ]; then
  echo "Base branch: $BASE_BRANCH"
else
  echo "Base branch: (undetected)"
fi
echo ""

# --- 1. Gate files (prerequisite, no points) ---
echo "📋 Gate Files"
for gate in survey plan scout build; do
  file=".pathfinder/${gate}.json"
  if [ ! -f "$file" ]; then
    echo "  ✘ Missing: $file"
    ERRORS=$((ERRORS + 1))
  else
    status=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('status','?'))" "$file")
    if [ "$status" = "approved" ] || [ "$status" = "complete" ]; then
      echo "  ✓ $file ($status)"
    else
      echo "  ✘ $file: status=$status (expected approved/complete)"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done
echo ""

if [ "$ERRORS" -gt 0 ]; then
  echo "✘ Gate files incomplete. Cannot compute quality score."
  exit 1
fi

# --- 2. Task files: evidence check (20 pts) + verified check (10 pts) ---
echo "📋 Task Evidence"
TASK_COUNT=0
EVIDENCE_COUNT=0
VERIFIED_COUNT=0
for task_file in .pathfinder/tasks/*.json; do
  [ -f "$task_file" ] || continue
  TASK_COUNT=$((TASK_COUNT + 1))
  id=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['id'])" "$task_file")
  status=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['status'])" "$task_file")
  has_evidence=$(python3 -c "
import json,sys
t = json.load(open(sys.argv[1]))
print('yes' if t.get('evidence',{}).get('green') else 'no')
" "$task_file")
  if [ "$has_evidence" = "yes" ]; then
    EVIDENCE_COUNT=$((EVIDENCE_COUNT + 1))
    echo "  ✓ $id ($status) — evidence present"
  else
    echo "  ⚠ $id ($status) — NO evidence"
  fi
  if [ "$status" = "verified" ]; then
    VERIFIED_COUNT=$((VERIFIED_COUNT + 1))
  fi
done

if [ "$TASK_COUNT" -gt 0 ]; then
  EVIDENCE_SCORE=$(( 20 * EVIDENCE_COUNT / TASK_COUNT ))
  VERIFIED_SCORE=$(( 10 * VERIFIED_COUNT / TASK_COUNT ))
else
  EVIDENCE_SCORE=0
  VERIFIED_SCORE=0
fi
SCORE=$(( SCORE + EVIDENCE_SCORE + VERIFIED_SCORE ))
echo "  Evidence: $EVIDENCE_COUNT/$TASK_COUNT ($EVIDENCE_SCORE/20 pts)"
echo "  Verified: $VERIFIED_COUNT/$TASK_COUNT ($VERIFIED_SCORE/10 pts)"
echo ""

# --- 3. Run tests (25 pts for checkpoint tests, 20 pts for no regressions) ---
echo "📋 Test Suite"
CHECKPOINT_SCORE=0
REGRESSION_SCORE=0
TESTS_DETAIL=""
if npm run test:all > "$TEST_OUTPUT" 2>&1; then
  echo "  ✓ All tests pass"
  CHECKPOINT_SCORE=25
  REGRESSION_SCORE=20
  TESTS_DETAIL=$(tail -5 "$TEST_OUTPUT")
else
  echo "  ✘ Tests failed"
  TESTS_DETAIL=$(tail -10 "$TEST_OUTPUT")
fi
SCORE=$(( SCORE + CHECKPOINT_SCORE + REGRESSION_SCORE ))
echo "$TESTS_DETAIL" | sed 's/^/  /'
echo ""

# --- 4. Branch hygiene (15 pts) ---
echo "📋 Branch Hygiene"
BRANCH_SCORE=0
if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "master" ]; then
  echo "  ✓ On feature branch: $BRANCH"
  BRANCH_SCORE=15
else
  echo "  ✘ On $BRANCH — must use feature branch"
fi
SCORE=$(( SCORE + BRANCH_SCORE ))
echo ""

# --- 5. PR created (10 pts) ---
echo "📋 Pull Request"
PR_SCORE=0
PR_URL=$(gh pr list --head "$BRANCH" --json url --jq '.[0].url' 2>/dev/null || echo "")
if [ -n "$PR_URL" ]; then
  echo "  ✓ PR exists: $PR_URL"
  PR_SCORE=10
else
  echo "  ⚠ No PR found for branch $BRANCH"
fi
SCORE=$(( SCORE + PR_SCORE ))
echo ""

# --- 6. Security check ---
echo "📋 Security"
if [ -n "$BASE_BRANCH" ]; then
  secrets=$(git diff --name-only "$BASE_BRANCH"..HEAD 2>/dev/null | grep -E '\.env$|\.env\.local|secrets|credentials' || true)
else
  secrets=$(git diff --name-only HEAD~1..HEAD 2>/dev/null | grep -E '\.env$|\.env\.local|secrets|credentials' || true)
fi
if [ -n "$secrets" ]; then
  echo "  ✘ Potential secrets in diff: $secrets"
else
  echo "  ✓ No secret files in diff"
fi
echo ""

# --- Summary ---
echo "================================================"
echo "Quality Score: $SCORE / $MAX_SCORE"
if [ "$SCORE" -ge 90 ]; then
  echo "🟢 Excellent — merge-ready"
elif [ "$SCORE" -ge 70 ]; then
  echo "🟡 Acceptable — review carefully"
else
  echo "🔴 Below threshold — fix issues before merge"
fi

# --- Write report.json ---
PR_URL_JSON="${PR_URL:-null}"
if [ "$PR_URL_JSON" != "null" ]; then
  PR_URL_JSON="\"$PR_URL_JSON\""
fi

mkdir -p .pathfinder
cat > .pathfinder/report.json << EOF_JSON
{
  "phase": "report",
  "status": "complete",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "qualityScore": $SCORE,
  "breakdown": {
    "allTestsPass": {"score": $CHECKPOINT_SCORE, "max": 25},
    "evidenceComplete": {"score": $EVIDENCE_SCORE, "max": 20},
    "noRegressions": {"score": $REGRESSION_SCORE, "max": 20},
    "branchHygiene": {"score": $BRANCH_SCORE, "max": 15},
    "prCreated": {"score": $PR_SCORE, "max": 10},
    "allVerified": {"score": $VERIFIED_SCORE, "max": 10}
  },
  "pr": {"url": $PR_URL_JSON}
}
EOF_JSON
echo ""
echo "Report saved to .pathfinder/report.json"

exit $(( SCORE < 70 ? 1 : 0 ))
