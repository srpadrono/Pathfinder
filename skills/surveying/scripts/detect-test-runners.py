#!/usr/bin/env python3
"""Detect test frameworks in the current project. Outputs JSON to stdout."""
import json, os, sys

e2e = "none"
unit = "none"

checks = [
    ("playwright.config.ts", "e2e", "playwright"),
    ("playwright.config.js", "e2e", "playwright"),
    ("cypress.config.ts", "e2e", "cypress"),
    ("cypress.config.js", "e2e", "cypress"),
    ("e2e/.maestro/config.yaml", "e2e", "maestro"),
    (".detoxrc.js", "e2e", "detox"),
    ("vitest.config.ts", "unit", "vitest"),
    ("vitest.config.js", "unit", "vitest"),
    ("jest.config.ts", "unit", "jest"),
    ("jest.config.js", "unit", "jest"),
    ("jest.config.json", "unit", "jest"),
    ("pytest.ini", "unit", "pytest"),
    ("go.mod", "unit", "gotest"),
    ("Package.swift", "unit", "xctest"),
]

root = sys.argv[1] if len(sys.argv) > 1 else "."

for path, kind, runner in checks:
    if os.path.exists(os.path.join(root, path)):
        if kind == "e2e" and e2e == "none":
            e2e = runner
        elif kind == "unit" and unit == "none":
            unit = runner

# Check pyproject.toml for pytest
if unit == "none" and os.path.exists(os.path.join(root, "pyproject.toml")):
    with open(os.path.join(root, "pyproject.toml")) as f:
        if "pytest" in f.read():
            unit = "pytest"

result = {"e2e": e2e, "unit": unit}
print(json.dumps(result))
if e2e == "none" and unit == "none":
    print("WARNING: No test frameworks detected", file=sys.stderr)
    sys.exit(1)
