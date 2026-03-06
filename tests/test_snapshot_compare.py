#!/usr/bin/env python3
"""Tests for snapshot-compare.py"""
import base64, subprocess, json, tempfile, os

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "skills", "pathfinder", "scripts", "snapshot-compare.py")

def create_test_image(path, size=100, color=(255, 0, 0)):
    """Create a simple PNG. Falls back to a valid embedded 1x1 PNG."""
    try:
        from PIL import Image
        img = Image.new("RGB", (size, size), color)
        img.save(path)
    except ImportError:
        # 1x1 transparent PNG
        png_bytes = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO9Wl1EAAAAASUVORK5CYII="
        )
        with open(path, "wb") as f:
            f.write(png_bytes)

def test_capture():
    with tempfile.TemporaryDirectory() as d:
        img = os.path.join(d, "screen.png")
        create_test_image(img)
        r = subprocess.run(["python3", SCRIPT, "capture", "login", img], cwd=d, capture_output=True, text=True)
        assert r.returncode == 0
        out = json.loads(r.stdout)
        assert out["action"] == "capture"
        assert os.path.exists(out["baseline"])
    print("✅ test_capture")

def test_compare_identical():
    with tempfile.TemporaryDirectory() as d:
        img = os.path.join(d, "screen.png")
        create_test_image(img)
        subprocess.run(["python3", SCRIPT, "capture", "test", img], cwd=d, capture_output=True)
        r = subprocess.run(["python3", SCRIPT, "compare", "test", img], cwd=d, capture_output=True, text=True)
        assert r.returncode == 0
        out = json.loads(r.stdout)
        assert out["passed"] is True
        assert out["diffPercent"] == 0.0
    print("✅ test_compare_identical")

def test_no_baseline():
    with tempfile.TemporaryDirectory() as d:
        img = os.path.join(d, "screen.png")
        create_test_image(img)
        r = subprocess.run(["python3", SCRIPT, "compare", "nonexistent", img], cwd=d, capture_output=True, text=True)
        assert r.returncode == 1
        out = json.loads(r.stdout)
        assert "no baseline" in out.get("error", "")
    print("✅ test_no_baseline")

if __name__ == "__main__":
    test_capture()
    test_compare_identical()
    test_no_baseline()
    print("\nAll snapshot-compare tests passed")
