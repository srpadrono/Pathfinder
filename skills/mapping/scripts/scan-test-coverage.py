#!/usr/bin/env python3
"""Scan a project for existing UI/E2E test files and map them to routes/screens.

Usage: python3 scan-test-coverage.py <project-root>

Outputs JSON with discovered test files and the routes/screens they reference.
"""
import os, sys, json, re, glob

root = sys.argv[1] if len(sys.argv) > 1 else "."

# Common test directories and patterns
test_patterns = [
    "e2e/**/*.spec.ts", "e2e/**/*.spec.js",
    "e2e/**/*.test.ts", "e2e/**/*.test.js",
    "e2e/**/*.yaml", "e2e/**/*.yml",  # Maestro
    "cypress/e2e/**/*.cy.ts", "cypress/e2e/**/*.cy.js",
    "integration_test/**/*_test.dart",  # Flutter
    "**/*UITests*.swift",  # XCUITest
    "**/*Test.kt", "**/*Test.java",  # Espresso
    "__tests__/**/*.test.tsx", "__tests__/**/*.test.ts",  # RN/Jest
    "tests/**/*.test.tsx", "tests/**/*.test.ts",
    "**/*.spec.tsx", "**/*.spec.ts",
]

# Patterns to extract routes/screens from test content
route_patterns = [
    re.compile(r'(?:goto|visit|navigate)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]'),  # Playwright/Cypress
    re.compile(r'(?:launchApp|openApp)', re.IGNORECASE),  # Mobile
    re.compile(r'tapOn:\s*[\'"]?([^\'"\n]+)'),  # Maestro
    re.compile(r'(?:getByTestId|getByRole|getByText)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]'),  # Playwright
    re.compile(r'cy\.get\s*\(\s*[\'"`]([^\'"`]+)[\'"`]'),  # Cypress
    re.compile(r'element\(by\.\w+\([\'"`]([^\'"`]+)[\'"`]\)\)'),  # Detox
    re.compile(r'find\.(?:byKey|text|byType)\s*\(\s*(?:const Key\()?\s*[\'"`]?([^\'"`\)]+)'),  # Flutter
]

test_files = []
for pattern in test_patterns:
    for f in glob.glob(os.path.join(root, pattern), recursive=True):
        rel = os.path.relpath(f, root)
        # Skip node_modules
        if "node_modules" in rel:
            continue

        refs = []
        try:
            with open(f) as fh:
                content = fh.read()
            for rp in route_patterns:
                refs.extend(rp.findall(content))
        except (UnicodeDecodeError, PermissionError):
            pass

        test_files.append({
            "file": rel,
            "references": list(set(refs))[:20],  # cap to avoid noise
        })

# Also scan for route/screen definitions
routes = []
route_files = glob.glob(os.path.join(root, "app/**/page.tsx"), recursive=True) + \
              glob.glob(os.path.join(root, "app/**/page.ts"), recursive=True) + \
              glob.glob(os.path.join(root, "pages/**/*.tsx"), recursive=True) + \
              glob.glob(os.path.join(root, "app/**/*.tsx"), recursive=True) + \
              glob.glob(os.path.join(root, "lib/routes/**/*.dart"), recursive=True)

for f in route_files:
    rel = os.path.relpath(f, root)
    if "node_modules" in rel or "__tests__" in rel or ".test." in rel:
        continue
    routes.append(rel)

result = {
    "testFiles": test_files,
    "totalTestFiles": len(test_files),
    "routeFiles": routes[:50],
    "totalRouteFiles": len(routes),
}

print(json.dumps(result, indent=2))

if not test_files:
    print("WARNING: No UI test files found", file=sys.stderr)
