#!/usr/bin/env python3
"""Initialize Pathfinder in a project.

Usage: python3 pathfinder-init.py [--name project-name]
"""
import argparse, json, os, sys, subprocess, datetime, re

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
    detect = os.path.join(script_dir, "detect-ui-framework.py")

    detection = {"uiFramework": "unknown", "unitRunner": "unknown", "platform": "unknown"}
    if os.path.exists(detect):
        result = subprocess.run(["python3", detect, "."], capture_output=True, text=True)
        if result.returncode == 0:
            detection = json.loads(result.stdout)

    os.makedirs(".pathfinder", exist_ok=True)

    # Detect test directory
    test_dir = None
    for cfg in ["e2e/playwright.config.ts", "playwright.config.ts", "cypress.config.ts"]:
        if os.path.exists(cfg):
            with open(cfg) as f:
                content = f.read()
            m = re.search(r"testDir:\s*['\"]\.?/?([^'\"]+)['\"]", content)
            if m:
                base = os.path.dirname(cfg)
                test_dir = os.path.join(base, m.group(1)) if base else m.group(1)
            else:
                test_dir = os.path.dirname(cfg) or "e2e"
            break

    config = {
        "version": "2.0.0",
        "project": name,
        "framework": detection.get("uiFramework", "unknown"),
        "platform": detection.get("platform", "unknown"),
        "unitRunner": detection.get("unitRunner", "unknown"),
        "created": datetime.datetime.utcnow().isoformat() + "Z",
    }
    if test_dir:
        config["testDir"] = test_dir

    for cfg in ["e2e/playwright.config.ts", "playwright.config.ts"]:
        if os.path.exists(cfg):
            with open(cfg) as f:
                if "storageState" in f.read():
                    config["auth"] = {"storageState": "auto-detected"}
            break

    with open(".pathfinder/config.json", "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Pathfinder initialized for '{name}'")
    print(f"   Config: .pathfinder/config.json")
    print(f"   UI framework: {config['framework']}")
    print(f"   Platform: {config['platform']}")
    if test_dir:
        print(f"   Test directory: {test_dir}")
    print(f"\n   Next: /map to discover user journeys")

if __name__ == "__main__":
    main()
