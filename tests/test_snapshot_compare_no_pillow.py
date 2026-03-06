#!/usr/bin/env python3
"""Tests for snapshot-compare.py hash-based fallback when Pillow is unavailable."""
import base64
import json
import os
import subprocess
import tempfile

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "skills", "pathfinder", "scripts", "snapshot-compare.py")
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills", "pathfinder", "scripts")

# A valid 1x1 red PNG
PNG_RED = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADklEQVQI12P4z8BQDwAEgAF/"
    "QualIQAAAABJRU5ErkJggg=="
)

# A valid 1x1 transparent PNG (different from red)
PNG_TRANSPARENT = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO9Wl1EAAAAASUVORK5CYII="
)

# Wrapper that blocks PIL imports, then runs snapshot-compare.py via runpy
WRAPPER_CODE = """\
import sys, runpy

class PILBlocker:
    def find_spec(self, fullname, path, target=None):
        if fullname == "PIL" or fullname.startswith("PIL."):
            raise ImportError("Mocked: Pillow not installed")
        return None

sys.meta_path.insert(0, PILBlocker())

# Remove any cached PIL modules
for key in list(sys.modules.keys()):
    if key == "PIL" or key.startswith("PIL."):
        del sys.modules[key]

# The real script path is passed as the first arg after -c
script = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(script, run_name="__main__")
"""


def run_no_pillow(args, cwd):
    """Run snapshot-compare.py with PIL mocked out via a wrapper."""
    env = os.environ.copy()
    # Ensure pathfinder_paths is importable
    env["PYTHONPATH"] = SCRIPTS_DIR + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        ["python3", "-c", WRAPPER_CODE, SCRIPT] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
    )


def test_capture_without_pillow():
    """Capture should work without Pillow (just copies the file)."""
    with tempfile.TemporaryDirectory() as d:
        img = os.path.join(d, "screen.png")
        with open(img, "wb") as f:
            f.write(PNG_RED)
        r = run_no_pillow(["capture", "login", img], d)
        assert r.returncode == 0, f"Failed: {r.stderr}"
        out = json.loads(r.stdout)
        assert out["action"] == "capture"
        assert os.path.exists(out["baseline"])
        assert "hash" in out
    print("pass: test_capture_without_pillow")


def test_compare_identical_without_pillow():
    """Identical images should pass with hash method when Pillow unavailable."""
    with tempfile.TemporaryDirectory() as d:
        img = os.path.join(d, "screen.png")
        with open(img, "wb") as f:
            f.write(PNG_RED)
        # Capture baseline
        run_no_pillow(["capture", "hashtest", img], d)
        # Compare same image
        r = run_no_pillow(["compare", "hashtest", img], d)
        assert r.returncode == 0, f"Failed: {r.stderr}"
        out = json.loads(r.stdout)
        assert out["passed"] is True
        assert out["diffPercent"] == 0.0
        assert out["method"] == "hash"
    print("pass: test_compare_identical_without_pillow")


def test_compare_different_without_pillow():
    """Different images should fail with hash method (reports 100% diff)."""
    with tempfile.TemporaryDirectory() as d:
        img1 = os.path.join(d, "baseline.png")
        img2 = os.path.join(d, "current.png")
        with open(img1, "wb") as f:
            f.write(PNG_RED)
        with open(img2, "wb") as f:
            f.write(PNG_TRANSPARENT)
        # Capture baseline
        run_no_pillow(["capture", "difftest", img1], d)
        # Compare different image
        r = run_no_pillow(["compare", "difftest", img2], d)
        # Should fail because diff exceeds default threshold
        assert r.returncode == 1, f"Expected failure for different images, got rc={r.returncode}"
        out = json.loads(r.stdout)
        assert out["passed"] is False
        assert out["diffPercent"] == 100.0
        assert out["method"] == "hash"
    print("pass: test_compare_different_without_pillow")


def test_hash_fallback_warning_message():
    """When images differ and Pillow is unavailable, a warning should be printed."""
    with tempfile.TemporaryDirectory() as d:
        img1 = os.path.join(d, "baseline.png")
        img2 = os.path.join(d, "current.png")
        with open(img1, "wb") as f:
            f.write(PNG_RED)
        with open(img2, "wb") as f:
            f.write(PNG_TRANSPARENT)
        run_no_pillow(["capture", "warntest", img1], d)
        r = run_no_pillow(["compare", "warntest", img2], d)
        assert "Pillow not installed" in r.stderr
        assert "hash comparison" in r.stderr
    print("pass: test_hash_fallback_warning_message")


if __name__ == "__main__":
    test_capture_without_pillow()
    test_compare_identical_without_pillow()
    test_compare_different_without_pillow()
    test_hash_fallback_warning_message()
    print("\nAll snapshot-compare-no-pillow tests passed")
