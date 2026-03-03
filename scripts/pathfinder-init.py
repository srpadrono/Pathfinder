#!/usr/bin/env python3
"""Initialize a Pathfinder expedition in one command.

Usage: python3 pathfinder-init.py <expedition-name> [--no-branch]

Creates: feature branch, .pathfinder/state.json, detects frameworks.
"""
import argparse, json, os, sys, subprocess, datetime

def run(cmd, check=True):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)

def main():
    parser = argparse.ArgumentParser(description="Initialize a Pathfinder expedition")
    parser.add_argument("name", help="Expedition name (e.g. login-flow)")
    parser.add_argument("--no-branch", action="store_true", help="Skip branch creation")
    args = parser.parse_args()

    name = args.name
    branch = f"feat/{name}"
    now = datetime.datetime.utcnow().isoformat() + "Z"

    # Check for existing expedition
    if os.path.exists(".pathfinder/state.json"):
        print(f"ERROR: Expedition already exists. Delete .pathfinder/ to start fresh.", file=sys.stderr)
        sys.exit(1)

    # Create branch
    if not args.no_branch:
        result = run(f"git checkout -b {branch}", check=False)
        if result.returncode != 0:
            if "already exists" in result.stderr:
                run(f"git checkout {branch}")
                print(f"Switched to existing branch: {branch}")
            else:
                print(f"ERROR: {result.stderr.strip()}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Created branch: {branch}")

    # Detect frameworks
    script_dir = os.path.dirname(os.path.abspath(__file__))
    detect_script = os.path.join(script_dir, "..", "skills", "ui-testing", "scripts", "detect-ui-framework.py")
    if not os.path.exists(detect_script):
        detect_script = os.path.join(script_dir, "detect-ui-framework.py")

    detection = {"uiFramework": "unknown", "unitRunner": "unknown"}
    if os.path.exists(detect_script):
        result = run(f"python3 {detect_script} .", check=False)
        if result.returncode == 0:
            detection = json.loads(result.stdout)

    # Create state
    os.makedirs(".pathfinder/tasks", exist_ok=True)

    state = {
        "version": "0.6.0",
        "expedition": name,
        "branch": branch,
        "currentPhase": "survey",
        "testRunners": {
            "e2e": detection.get("uiFramework", "unknown"),
            "unit": detection.get("unitRunner", "unknown"),
        },
        "phases": {
            "survey":  {"status": "pending", "timestamp": None},
            "plan":    {"status": "pending", "timestamp": None},
            "scout":   {"status": "pending", "timestamp": None},
            "build":   {"status": "pending", "timestamp": None},
            "report":  {"status": "pending", "timestamp": None},
        },
        "checkpoints": {"total": 0, "planned": 0, "red": 0, "green": 0, "verified": 0}
    }

    with open(".pathfinder/state.json", "w") as f:
        json.dump(state, f, indent=2)

    print(f"\n✅ Expedition '{name}' initialized")
    print(f"   Branch: {branch}")
    print(f"   UI framework: {detection.get('uiFramework', 'unknown')}")
    print(f"   Unit runner: {detection.get('unitRunner', 'unknown')}")
    print(f"\n   Next: approve survey → pathfinder:surveying")

if __name__ == "__main__":
    main()
