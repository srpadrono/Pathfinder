#!/usr/bin/env python3
"""Initialize a Pathfinder session for UI test coverage mapping.

Usage: python3 pathfinder-init.py [--name project-name]
"""
import argparse, json, os, sys, subprocess, datetime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="Project name (default: current dir name)")
    args = parser.parse_args()

    name = args.name or os.path.basename(os.getcwd())

    if os.path.exists(".pathfinder/journeys.json"):
        print(f"Pathfinder already initialized. Run /map to update journeys.", file=sys.stderr)
        sys.exit(1)

    # Detect UI framework
    script_dir = os.path.dirname(os.path.abspath(__file__))
    detect = os.path.join(script_dir, "..", "skills", "ui-testing", "scripts", "detect-ui-framework.py")

    detection = {"uiFramework": "unknown", "unitRunner": "unknown", "platform": "unknown"}
    if os.path.exists(detect):
        result = subprocess.run(["python3", detect, "."], capture_output=True, text=True)
        if result.returncode == 0:
            detection = json.loads(result.stdout)

    os.makedirs(".pathfinder", exist_ok=True)

    state = {
        "version": "1.0.0",
        "project": name,
        "framework": detection.get("uiFramework", "unknown"),
        "platform": detection.get("platform", "unknown"),
        "unitRunner": detection.get("unitRunner", "unknown"),
        "created": datetime.datetime.utcnow().isoformat() + "Z",
        "journeys": 0,
        "coverage": 0,
    }

    with open(".pathfinder/state.json", "w") as f:
        json.dump(state, f, indent=2)

    print(f"✅ Pathfinder initialized for '{name}'")
    print(f"   UI framework: {detection.get('uiFramework', 'unknown')}")
    print(f"   Platform: {detection.get('platform', 'unknown')}")
    print(f"   Unit runner: {detection.get('unitRunner', 'unknown')}")
    print(f"\n   Next: /map to discover user journeys")

if __name__ == "__main__":
    main()
