#!/usr/bin/env python3
"""Detect UI test framework from project files. Outputs JSON to stdout."""
from __future__ import annotations

import json
import os
import sys


def main() -> None:
    root = sys.argv[1] if len(sys.argv) > 1 else "."

    detections: list[tuple[str, str, str]] = [
        # (file_to_check, framework, platform)
        ("playwright.config.ts", "playwright", "web"),
        ("playwright.config.js", "playwright", "web"),
        ("cypress.config.ts", "cypress", "web"),
        ("cypress.config.js", "cypress", "web"),
        ("cypress.json", "cypress", "web"),
        (".detoxrc.js", "detox", "react-native"),
        (".detoxrc.json", "detox", "react-native"),
        ("e2e/.maestro/config.yaml", "maestro", "mobile"),
        ("integration_test/", "flutter-test", "flutter"),
        ("pubspec.yaml", "flutter-test", "flutter"),
    ]

    # Check for specific frameworks
    framework: str | None = None
    platform: str | None = None

    for path, fw, plat in detections:
        full = os.path.join(root, path)
        if os.path.exists(full):
            framework = fw
            platform = plat
            break

    # Fallback: detect by project type
    if not framework:
        if os.path.exists(os.path.join(root, "app.json")):
            # React Native / Expo
            try:
                with open(os.path.join(root, "app.json")) as f:
                    app_json = json.load(f)
                if "expo" in app_json:
                    framework = "maestro"
                    platform = "react-native"
            except (json.JSONDecodeError, KeyError):
                pass

        elif any(
            os.path.exists(os.path.join(root, f))
            for f in ["next.config.js", "next.config.ts", "next.config.mjs"]
        ):
            framework = "playwright"
            platform = "web"

        elif any(os.path.exists(os.path.join(root, f)) for f in ["vite.config.ts", "vite.config.js"]):
            framework = "playwright"
            platform = "web"

        elif any(
            f.endswith(".xcodeproj") or f.endswith(".xcworkspace")
            for f in os.listdir(root) if not f.startswith(".")
        ):
            framework = "xcuitest"
            platform = "ios"

        elif any(
            os.path.exists(os.path.join(root, f))
            for f in ["build.gradle", "build.gradle.kts"]
        ):
            framework = "espresso"
            platform = "android"

        elif os.path.exists(os.path.join(root, "Package.swift")):
            framework = "xcuitest"
            platform = "ios"

    # Also detect unit test runner
    unit_runner: str | None = None
    unit_checks: list[tuple[str, str]] = [
        ("vitest.config.ts", "vitest"), ("vitest.config.js", "vitest"),
        ("jest.config.ts", "jest"), ("jest.config.js", "jest"), ("jest.config.json", "jest"),
        ("pytest.ini", "pytest"), ("go.mod", "gotest"),
    ]
    for path, runner in unit_checks:
        if os.path.exists(os.path.join(root, path)):
            unit_runner = runner
            break
    if not unit_runner and os.path.exists(os.path.join(root, "pyproject.toml")):
        with open(os.path.join(root, "pyproject.toml")) as f:
            if "pytest" in f.read():
                unit_runner = "pytest"
    if not unit_runner and os.path.exists(os.path.join(root, "package.json")):
        with open(os.path.join(root, "package.json")) as f:
            pkg = json.load(f)
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "jest" in deps:
                unit_runner = "jest"
            elif "vitest" in deps:
                unit_runner = "vitest"

    result = {
        "uiFramework": framework or "unknown",
        "platform": platform or "unknown",
        "unitRunner": unit_runner or "unknown",
        "referenceFile": f"references/{framework}.md" if framework else None,
    }

    print(json.dumps(result, indent=2))

    if not framework:
        print("WARNING: No UI test framework detected. Install one or specify manually.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
