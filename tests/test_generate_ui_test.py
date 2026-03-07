#!/usr/bin/env python3
"""Tests for generate-ui-test.py"""
import json
import os
import subprocess
import tempfile

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
        with open(os.path.join(config_dir, "journeys.json"), "w") as f:
            json.dump({"journeys": []}, f)

        r = subprocess.run(
            ["python3", SCRIPT, "AUTH-01", "Login", "playwright", "--auto"],
            cwd=d,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"Failed: {r.stderr}"
        out = json.loads(r.stdout)
        expected_suffix = os.path.normpath(os.path.join("custom", "tests", "auth.spec.ts"))
        assert os.path.normpath(out["file"]).endswith(expected_suffix), out
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

def test_multiple_describe_blocks_appends_to_last():
    """When a file has multiple describe blocks, append should go into the last one."""
    with tempfile.TemporaryDirectory() as d:
        existing = os.path.join(d, "multi.spec.ts")
        with open(existing, "w") as f:
            f.write("""import { test, expect } from '@playwright/test'

test.describe('Setup', () => {
  test('setup step', async ({ page }) => {
    await page.goto('/setup')
  })
})

test.describe('Main Flow', () => {
  test('main test', async ({ page }) => {
    await page.goto('/main')
  })
})
""")
        r = subprocess.run(
            ["python3", SCRIPT, "MAIN-02", "New main test", "playwright",
             "--route", "/main", "--append", existing],
            capture_output=True, text=True,
        )
        assert r.returncode == 0, f"Failed: {r.stderr}"
        content = open(existing).read()
        assert "setup step" in content, "First describe block should remain"
        assert "main test" in content, "Second describe block original test should remain"
        assert "New main test" in content, "New test should be appended"
        # The new test should appear after "main test" (in the last describe block)
        assert content.find("New main test") > content.find("main test")
    print("pass: test_multiple_describe_blocks_appends_to_last")


def test_file_with_only_and_skip_tests():
    """Append should work in files containing .only() or .skip() tests."""
    with tempfile.TemporaryDirectory() as d:
        existing = os.path.join(d, "special.spec.ts")
        with open(existing, "w") as f:
            f.write("""import { test, expect } from '@playwright/test'

test.describe('Special', () => {
  test.only('focused test', async ({ page }) => {
    await page.goto('/focus')
  })

  test.skip('skipped test', async ({ page }) => {
    await page.goto('/skip')
  })
})
""")
        r = subprocess.run(
            ["python3", SCRIPT, "SPEC-03", "Normal test", "playwright",
             "--route", "/normal", "--append", existing],
            capture_output=True, text=True,
        )
        assert r.returncode == 0, f"Failed: {r.stderr}"
        content = open(existing).read()
        assert "test.only" in content, ".only() test should remain"
        assert "test.skip" in content, ".skip() test should remain"
        assert "Normal test" in content, "New test should be appended"
    print("pass: test_file_with_only_and_skip_tests")


def test_empty_describe_block():
    """Append to a file with an empty describe block."""
    with tempfile.TemporaryDirectory() as d:
        existing = os.path.join(d, "empty.spec.ts")
        with open(existing, "w") as f:
            f.write("""import { test, expect } from '@playwright/test'

test.describe('Empty', () => {
})
""")
        r = subprocess.run(
            ["python3", SCRIPT, "EMPTY-01", "First test", "playwright",
             "--route", "/first", "--append", existing],
            capture_output=True, text=True,
        )
        assert r.returncode == 0, f"Failed: {r.stderr}"
        content = open(existing).read()
        assert "First test" in content, "Test should be inserted into empty describe"
    print("pass: test_empty_describe_block")


def test_auto_path_uses_os_sep():
    """Verify auto-created file paths use os.path conventions (cross-platform)."""
    with tempfile.TemporaryDirectory() as d:
        config_dir = os.path.join(d, "my", "tests", "pathfinder")
        os.makedirs(config_dir)
        with open(os.path.join(config_dir, "config.json"), "w") as f:
            json.dump({"testDir": "my/tests"}, f)
        with open(os.path.join(config_dir, "journeys.json"), "w") as f:
            json.dump({"journeys": []}, f)

        r = subprocess.run(
            ["python3", SCRIPT, "NAV-01", "Navigate home", "playwright", "--auto"],
            cwd=d,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"Failed: {r.stderr}"
        out = json.loads(r.stdout)
        # Use os.path.normpath for cross-platform assertion
        expected_suffix = os.path.normpath(os.path.join("my", "tests", "nav.spec.ts"))
        assert os.path.normpath(out["file"]).endswith(expected_suffix), \
            f"Expected path ending with {expected_suffix}, got {out['file']}"
    print("pass: test_auto_path_uses_os_sep")


if __name__ == "__main__":
    test_create_playwright()
    test_create_maestro()
    test_append_playwright()
    test_auto_creates_when_no_match()
    test_auto_uses_initialized_pathfinder_config()
    test_append_playwright_with_semicolons_stays_in_describe()
    test_multiple_describe_blocks_appends_to_last()
    test_file_with_only_and_skip_tests()
    test_empty_describe_block()
    test_auto_path_uses_os_sep()
    print("\nAll generate-ui-test tests passed")
