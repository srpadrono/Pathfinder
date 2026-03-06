#!/usr/bin/env python3
"""Initialize Pathfinder in a project.

Usage: python3 pathfinder-init.py [--name project-name] [--output-dir path]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone


def detect_test_dir() -> str | None:
    """Auto-detect test directory from framework configs."""
    for cfg in ["e2e/playwright.config.ts", "playwright.config.ts", "cypress.config.ts"]:
        if os.path.exists(cfg):
            with open(cfg) as f:
                content = f.read()
            m = re.search(r"testDir:\s*['\"]\.?/?([^'\"]+)['\"]", content)
            if m:
                base = os.path.dirname(cfg)
                return os.path.join(base, m.group(1)) if base else m.group(1)
            else:
                return os.path.dirname(cfg) or "e2e"
    # Check for common test dirs
    for d in ["tests", "test", "__tests__", "e2e/tests", "e2e", "integration_test"]:
        if os.path.isdir(d):
            return d
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="Project name (default: current dir name)")
    parser.add_argument("--output-dir", help="Where to create pathfinder/ (default: auto-detect test dir)")
    args = parser.parse_args()

    name = args.name or os.path.basename(os.getcwd())

    # Determine output directory
    if args.output_dir:
        pathfinder_dir = os.path.join(args.output_dir, "pathfinder")
    else:
        test_dir = detect_test_dir()
        if test_dir:
            pathfinder_dir = os.path.join(test_dir, "pathfinder")
        else:
            pathfinder_dir = "pathfinder"

    journeys_path = os.path.join(pathfinder_dir, "journeys.json")

    if os.path.exists(journeys_path):
        print(f"Pathfinder already initialized at {pathfinder_dir}/. Run /map to update journeys.", file=sys.stderr)
        sys.exit(1)

    # Detect UI framework
    script_dir = os.path.dirname(os.path.abspath(__file__))
    detect = os.path.join(script_dir, "detect-ui-framework.py")

    detection: dict[str, str] = {"uiFramework": "unknown", "unitRunner": "unknown", "platform": "unknown"}
    if os.path.exists(detect):
        result = subprocess.run(["python3", detect, "."], capture_output=True, text=True)
        if result.returncode == 0:
            detection = json.loads(result.stdout)
        else:
            print(
                f"WARNING: UI framework detection failed (exit {result.returncode}). "
                f"Falling back to 'unknown'. stderr: {result.stderr.strip()}",
                file=sys.stderr,
            )
    else:
        print(
            f"WARNING: detect-ui-framework.py not found at {detect}. "
            "Framework detection skipped, using 'unknown'.",
            file=sys.stderr,
        )

    os.makedirs(pathfinder_dir, exist_ok=True)

    # Detect test directory for config
    test_dir = detect_test_dir()

    # Detect auth pattern
    auth: dict[str, str] | None = None
    for cfg in ["e2e/playwright.config.ts", "playwright.config.ts"]:
        if os.path.exists(cfg):
            with open(cfg) as f:
                if "storageState" in f.read():
                    auth = {"storageState": "auto-detected"}
            break

    config: dict = {
        "version": "2.0.0",
        "project": name,
        "framework": detection.get("uiFramework", "unknown"),
        "platform": detection.get("platform", "unknown"),
        "unitRunner": detection.get("unitRunner", "unknown"),
        "created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if test_dir:
        config["testDir"] = test_dir
    if auth:
        config["auth"] = auth

    config_path = os.path.join(pathfinder_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Pathfinder initialized for '{name}'")
    print(f"   Directory: {pathfinder_dir}/")
    print(f"   Config: {config_path}")
    print(f"   UI framework: {config['framework']}")
    print(f"   Platform: {config['platform']}")
    if test_dir:
        print(f"   Test directory: {test_dir}")
    print("\n   Next: /map to discover user journeys")


if __name__ == "__main__":
    main()
