#!/usr/bin/env python3
"""Compute expedition quality score (0-100). Outputs JSON report to stdout."""
import json, glob, sys, os, subprocess

tasks_dir = sys.argv[1] if len(sys.argv) > 1 else ".pathfinder/tasks"
state_file = sys.argv[2] if len(sys.argv) > 2 else ".pathfinder/state.json"

tasks = []
for f in sorted(glob.glob(os.path.join(tasks_dir, "*.json"))):
    tasks.append(json.load(open(f)))

total = len(tasks)
if total == 0:
    print('{"error": "No task files found"}')
    sys.exit(1)

# 1. All tests pass (25pts)
all_green = all(t.get("status") in ("green", "verified") for t in tasks)
tests_score = 25 if all_green else 0

# 2. Evidence complete (15pts)
with_evidence = sum(1 for t in tasks if t.get("evidence", {}).get("green"))
evidence_score = round(15 * with_evidence / total)

# 3. No regressions (20pts) - check for build gate
has_build_gate = os.path.exists(".pathfinder/build.json")
regression_score = 20 if has_build_gate else 0

# 4. Branch hygiene (10pts)
try:
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    on_feature = branch not in ("main", "master", "")
except Exception:
    on_feature = False
branch_score = 10 if on_feature else 0

# 5. PR created (10pts)
try:
    pr_out = subprocess.check_output(["gh", "pr", "list", "--head", branch, "--json", "number"], text=True)
    has_pr = len(json.loads(pr_out)) > 0
except Exception:
    has_pr = False
pr_score = 10 if has_pr else 0

# 6. All verified (10pts)
all_verified = all(t.get("status") == "verified" for t in tasks)
verified_score = 10 if all_verified else 0

# 7. Documentation (10pts) - check for plan file
state = json.load(open(state_file)) if os.path.exists(state_file) else {}
has_plan = os.path.exists(".pathfinder/plan.json")
doc_score = 10 if has_plan else 0

total_score = tests_score + evidence_score + regression_score + branch_score + pr_score + verified_score + doc_score

report = {
    "qualityScore": total_score,
    "breakdown": {
        "allTestsPass": {"score": tests_score, "max": 25},
        "evidenceComplete": {"score": evidence_score, "max": 15},
        "noRegressions": {"score": regression_score, "max": 20},
        "branchHygiene": {"score": branch_score, "max": 10},
        "prCreated": {"score": pr_score, "max": 10},
        "allVerified": {"score": verified_score, "max": 10},
        "documentation": {"score": doc_score, "max": 10}
    },
    "tasksTotal": total,
    "tasksVerified": sum(1 for t in tasks if t.get("status") == "verified"),
    "tasksGreen": sum(1 for t in tasks if t.get("status") in ("green", "verified")),
}

print(json.dumps(report, indent=2))

if total_score >= 90:
    print("🟢 EXCELLENT — merge-ready", file=sys.stderr)
elif total_score >= 70:
    print("🟡 ACCEPTABLE — review carefully", file=sys.stderr)
else:
    print("🔴 DO NOT MERGE — fix issues first", file=sys.stderr)
    sys.exit(1)
