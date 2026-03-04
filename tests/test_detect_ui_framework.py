#!/usr/bin/env python3
"""Tests for detect-ui-framework.py"""
import subprocess, json, tempfile, os, sys

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "detect-ui-framework.py")

def run(tmpdir):
    r = subprocess.run(["python3", SCRIPT, tmpdir], capture_output=True, text=True)
    return r.returncode, json.loads(r.stdout) if r.stdout.strip() else {}

def test_playwright():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "playwright.config.ts"), "w").close()
        code, out = run(d)
        assert code == 0, f"Expected 0, got {code}"
        assert out["uiFramework"] == "playwright"
        assert out["platform"] == "web"
    print("✅ test_playwright")

def test_nextjs_fallback():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "next.config.js"), "w").close()
        code, out = run(d)
        assert code == 0
        assert out["uiFramework"] == "playwright"
    print("✅ test_nextjs_fallback")

def test_expo():
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "app.json"), "w") as f:
            json.dump({"expo": {"name": "test"}}, f)
        code, out = run(d)
        assert code == 0
        assert out["uiFramework"] == "maestro"
    print("✅ test_expo")

def test_cypress():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "cypress.config.ts"), "w").close()
        code, out = run(d)
        assert code == 0
        assert out["uiFramework"] == "cypress"
    print("✅ test_cypress")

def test_flutter():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "pubspec.yaml"), "w").close()
        os.makedirs(os.path.join(d, "integration_test"))
        code, out = run(d)
        assert code == 0
        assert out["uiFramework"] == "flutter-test"
    print("✅ test_flutter")

def test_unknown():
    with tempfile.TemporaryDirectory() as d:
        code, out = run(d)
        assert code == 1
        assert out["uiFramework"] == "unknown"
    print("✅ test_unknown")

def test_unit_runner_jest():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "playwright.config.ts"), "w").close()
        with open(os.path.join(d, "package.json"), "w") as f:
            json.dump({"devDependencies": {"jest": "^29"}}, f)
        code, out = run(d)
        assert out["unitRunner"] == "jest"
    print("✅ test_unit_runner_jest")

if __name__ == "__main__":
    test_playwright()
    test_nextjs_fallback()
    test_expo()
    test_cypress()
    test_flutter()
    test_unknown()
    test_unit_runner_jest()
    print("\nAll detect-ui-framework tests passed")
