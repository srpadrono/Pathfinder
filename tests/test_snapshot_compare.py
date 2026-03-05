#!/usr/bin/env python3
"""Tests for snapshot-compare.py"""
import subprocess, json, tempfile, os

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "skills", "pathfinder", "scripts", "snapshot-compare.py")

def create_test_image(path, size=100, color=(255, 0, 0)):
    """Create a simple PNG. Falls back to copying a 1-byte file if no Pillow."""
    try:
        from PIL import Image
        img = Image.new("RGB", (size, size), color)
        img.save(path)
    except ImportError:
        # Create a minimal valid file
        with open(path, "wb") as f:
            f.write(b"\x89PNG" + os.urandom(100))

def test_capture():
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        img = os.path.join(d, "screen.png")
        create_test_image(img)
        r = subprocess.run(["python3", SCRIPT, "capture", "login", img], capture_output=True, text=True)
        assert r.returncode == 0
        out = json.loads(r.stdout)
        assert out["action"] == "capture"
        assert os.path.exists(out["baseline"])
    print("✅ test_capture")

def test_compare_identical():
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        img = os.path.join(d, "screen.png")
        create_test_image(img)
        subprocess.run(["python3", SCRIPT, "capture", "test", img], capture_output=True)
        r = subprocess.run(["python3", SCRIPT, "compare", "test", img], capture_output=True, text=True)
        assert r.returncode == 0
        out = json.loads(r.stdout)
        assert out["passed"] is True
        assert out["diffPercent"] == 0.0
    print("✅ test_compare_identical")

def test_no_baseline():
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        img = os.path.join(d, "screen.png")
        create_test_image(img)
        r = subprocess.run(["python3", SCRIPT, "compare", "nonexistent", img], capture_output=True, text=True)
        assert r.returncode == 1
        out = json.loads(r.stdout)
        assert "no baseline" in out.get("error", "")
    print("✅ test_no_baseline")

if __name__ == "__main__":
    orig = os.getcwd()
    test_capture()
    test_compare_identical()
    test_no_baseline()
    os.chdir(orig)
    print("\nAll snapshot-compare tests passed")
