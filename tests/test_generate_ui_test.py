#!/usr/bin/env python3
"""Tests for generate-ui-test.py"""
import subprocess, json, tempfile, os

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "skills", "pathfinder", "scripts", "generate-ui-test.py")

def test_create_playwright():
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "test.spec.ts")
        r = subprocess.run(["python3", SCRIPT, "FEAT-01", "User logs in", "playwright",
                           "--route", "/login", "--output", out], capture_output=True, text=True)
        assert r.returncode == 0, f"Failed: {r.stderr}"
        content = open(out).read()
        assert "test('User logs in'" in content
        assert "page.goto('/login')" in content
        assert "import { test, expect }" in content
    print("✅ test_create_playwright")

def test_create_maestro():
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "flow.yaml")
        r = subprocess.run(["python3", SCRIPT, "CHAT-01", "Send message", "maestro",
                           "--output", out], capture_output=True, text=True)
        assert r.returncode == 0
        content = open(out).read()
        assert "launchApp" in content
        assert "Send message" in content
    print("✅ test_create_maestro")

def test_append_playwright():
    with tempfile.TemporaryDirectory() as d:
        existing = os.path.join(d, "auth.spec.ts")
        with open(existing, "w") as f:
            f.write("""import { test, expect } from '@playwright/test'

test.describe('Auth', () => {
  test('existing test', async ({ page }) => {
    await page.goto('/login')
  })
})
""")
        r = subprocess.run(["python3", SCRIPT, "AUTH-02", "Logout works", "playwright",
                           "--route", "/dashboard", "--append", existing], capture_output=True, text=True)
        assert r.returncode == 0
        content = open(existing).read()
        assert "existing test" in content, "Original test should remain"
        assert "Logout works" in content, "New test should be appended"
    print("✅ test_append_playwright")

def test_auto_creates_when_no_match():
    with tempfile.TemporaryDirectory() as d:
        test_dir = os.path.join(d, "e2e", "tests")
        os.makedirs(test_dir)
        r = subprocess.run(["python3", SCRIPT, "NEW-01", "New journey", "playwright",
                           "--auto", "--test-dir", test_dir], capture_output=True, text=True)
        assert r.returncode == 0
        out = json.loads(r.stdout)
        assert out["action"] == "create"
        assert os.path.exists(out["file"])
    print("✅ test_auto_creates_when_no_match")


def test_auto_uses_initialized_pathfinder_config():
    with tempfile.TemporaryDirectory() as d:
        config_dir = os.path.join(d, "custom", "tests", "pathfinder")
        os.makedirs(config_dir)
        with open(os.path.join(config_dir, "config.json"), "w") as f:
            json.dump({"testDir": "custom/tests"}, f)

        r = subprocess.run(
            ["python3", SCRIPT, "AUTH-01", "Login", "playwright", "--auto"],
            cwd=d,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"Failed: {r.stderr}"
        out = json.loads(r.stdout)
        assert out["file"].endswith(os.path.join("custom", "tests", "auth.spec.ts")), out
        assert os.path.exists(os.path.join(d, "custom", "tests", "auth.spec.ts"))
    print("✅ test_auto_uses_initialized_pathfinder_config")


def test_append_playwright_with_semicolons_stays_in_describe():
    with tempfile.TemporaryDirectory() as d:
        existing = os.path.join(d, "auth.spec.ts")
        with open(existing, "w") as f:
            f.write("""import { test, expect } from '@playwright/test';

test.describe('Auth', () => {
  test('existing test', async ({ page }) => {
    await page.goto('/login');
  });
});
""")
        r = subprocess.run(
            ["python3", SCRIPT, "AUTH-02", "Logout works", "playwright",
             "--route", "/dashboard", "--append", existing],
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"Failed: {r.stderr}"
        content = open(existing).read()
        assert "Logout works" in content
        assert content.find("test('Logout works'") < content.rfind("});"), content
    print("✅ test_append_playwright_with_semicolons_stays_in_describe")

if __name__ == "__main__":
    test_create_playwright()
    test_create_maestro()
    test_append_playwright()
    test_auto_creates_when_no_match()
    test_auto_uses_initialized_pathfinder_config()
    test_append_playwright_with_semicolons_stays_in_describe()
    print("\nAll generate-ui-test tests passed")
