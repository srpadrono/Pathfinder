#!/usr/bin/env python3
"""Scan a project for UI test files and map them to routes/screens.

Usage: python3 scan-test-coverage.py <project-root>

Outputs JSON with test files, the routes they test, and a coverage matrix.
"""
import os, sys, json, re, glob

root = sys.argv[1] if len(sys.argv) > 1 else "."

# --- Find all test files ---
test_globs = [
    "e2e/**/*.spec.ts", "e2e/**/*.spec.js", "e2e/**/*.spec.tsx",
    "e2e/**/*.test.ts", "e2e/**/*.test.js",
    "e2e/**/*.yaml", "e2e/**/*.yml",
    "cypress/e2e/**/*.cy.ts", "cypress/e2e/**/*.cy.js",
    "integration_test/**/*_test.dart",
    "**/*UITests*.swift", "**/*Test.kt", "**/*Test.java",
    "__tests__/**/*.test.tsx", "__tests__/**/*.test.ts",
]

# --- Find all route/screen files ---
route_globs = [
    "app/**/page.tsx", "app/**/page.ts", "app/**/page.jsx",
    "pages/**/*.tsx", "pages/**/*.ts",
    "app/**/*.tsx",  # Expo Router
    "lib/routes/**/*.dart",
]

def extract_routes_from_code(filepath):
    """Extract routes/URLs and UI elements referenced in a test file."""
    try:
        with open(filepath) as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return {"routes": [], "actions": [], "assertions": [], "describes": []}

    routes = list(set(re.findall(r'(?:goto|visit|navigate)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', content)))

    # Extract test descriptions (what the test actually tests)
    describes = list(set(re.findall(r'(?:describe|test\.describe)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', content)))

    # Extract individual test names
    test_names = list(set(re.findall(r'(?:test|it)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', content)))

    # Extract assertions (what elements are being checked)
    assertions = list(set(re.findall(r'getByRole\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', content)))
    assertions += list(set(re.findall(r'getByText\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', content)))
    assertions += list(set(re.findall(r'getByTestId\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', content)))
    assertions += list(set(re.findall(r'data-cy=[\'"`]([^\'"`]+)[\'"`]', content)))

    # Maestro
    assertions += list(set(re.findall(r'assertVisible:\s*[\'"]?([^\'"}\n]+)', content)))
    taps = list(set(re.findall(r'tapOn:\s*(?:\n\s+id:\s*)?[\'"]?([^\'"}\n]+)', content)))

    return {
        "routes": routes[:20],
        "describes": describes[:10],
        "testNames": test_names[:30],
        "assertions": list(set(assertions))[:20],
        "actions": taps[:10],
    }

def route_from_filepath(filepath):
    """Convert a file path to its likely route (e.g., app/dashboard/page.tsx → /dashboard)."""
    fp = filepath.replace("\\", "/")
    # Next.js app router
    m = re.match(r'app/(.+)/page\.\w+$', fp)
    if m:
        route = "/" + m.group(1)
        # Clean dynamic segments
        route = re.sub(r'\[([^\]]+)\]', r':\1', route)
        return route
    # Pages router
    m = re.match(r'pages/(.+)\.\w+$', fp)
    if m:
        route = "/" + m.group(1)
        route = re.sub(r'/index$', '', route)
        return route or "/"
    # Expo Router
    m = re.match(r'app/(.+)\.\w+$', fp)
    if m:
        route = "/" + m.group(1)
        route = re.sub(r'\[([^\]]+)\]', r':\1', route)
        route = re.sub(r'/_layout$', '', route)
        route = re.sub(r'/index$', '', route)
        return route or "/"
    return None

# Collect test files

def main():
    test_files = []
    for pattern in test_globs:
        for f in glob.glob(os.path.join(root, pattern), recursive=True):
            rel = os.path.relpath(f, root)
            if "node_modules" in rel:
                continue
            analysis = extract_routes_from_code(f)
            test_files.append({"file": rel, **analysis})

    # Collect routes
    routes = []
    for pattern in route_globs:
        for f in glob.glob(os.path.join(root, pattern), recursive=True):
            rel = os.path.relpath(f, root)
            if "node_modules" in rel or "__tests__" in rel or ".test." in rel or "_layout" in rel:
                continue
            route = route_from_filepath(rel)
            if route:
                routes.append({"file": rel, "route": route})

    # Build coverage matrix: which routes have tests?
    tested_routes = set()
    for tf in test_files:
        for r in tf.get("routes", []):
            # Normalize
            tested_routes.add(r.rstrip("/") or "/")

    coverage_matrix = []
    for r in routes:
        route_normalized = r["route"].rstrip("/") or "/"
        is_tested = route_normalized in tested_routes
        # Also check partial matches (e.g., /dashboard matches /dashboard/reports)
        if not is_tested:
            is_tested = any(route_normalized.startswith(tr) or tr.startswith(route_normalized)
                           for tr in tested_routes)
        coverage_matrix.append({
            "route": r["route"],
            "file": r["file"],
            "tested": is_tested,
        })

    tested_count = sum(1 for c in coverage_matrix if c["tested"])
    total_routes = len(coverage_matrix)

    result = {
        "testFiles": test_files,
        "totalTestFiles": len(test_files),
        "routes": coverage_matrix,
        "totalRoutes": total_routes,
        "testedRoutes": tested_count,
        "untestedRoutes": total_routes - tested_count,
        "routeCoverage": round(tested_count / total_routes * 100, 1) if total_routes else 0,
    }

    print(json.dumps(result, indent=2))

    if not test_files:
        print("WARNING: No UI test files found", file=sys.stderr)
    if total_routes:
        print(f"Route coverage: {tested_count}/{total_routes} ({result['routeCoverage']}%)", file=sys.stderr)


if __name__ == "__main__":
    main()
