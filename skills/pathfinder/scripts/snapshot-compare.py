#!/usr/bin/env python3
"""Visual regression: capture and compare screenshots.

Usage:
  python3 snapshot-compare.py capture <name> <image-path>
  python3 snapshot-compare.py compare <name> <image-path> [--threshold 5]

Baselines stored in <testDir>/pathfinder/baselines/ when Pathfinder is initialized.
Requires Pillow for pixel-level comparison. Falls back to hash comparison if unavailable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys

from pathfinder_paths import find_pathfinder_dir


def baselines_dir() -> str:
    return os.path.join(find_pathfinder_dir(), "baselines")

def file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def pixel_diff(baseline_path: str, current_path: str) -> float | None:
    """Compare two images pixel-by-pixel. Returns diff percentage (0-100)."""
    try:
        import math  # noqa: F401

        from PIL import Image
    except ImportError:
        return None  # Pillow not available

    img1 = Image.open(baseline_path).convert("RGB")
    img2 = Image.open(current_path).convert("RGB")

    # Resize to same dimensions if different
    if img1.size != img2.size:
        img2 = img2.resize(img1.size, Image.LANCZOS)

    pixels1 = list(img1.getdata())
    pixels2 = list(img2.getdata())
    total = len(pixels1)

    if total == 0:
        return 0.0

    diff_pixels = 0
    for p1, p2 in zip(pixels1, pixels2):
        # Consider a pixel different if any channel differs by > 10
        if any(abs(a - b) > 10 for a, b in zip(p1, p2)):
            diff_pixels += 1

    return round(diff_pixels / total * 100, 2)

def capture(name: str, image_path: str) -> None:
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    baseline_dir = baselines_dir()
    os.makedirs(baseline_dir, exist_ok=True)
    ext = os.path.splitext(image_path)[1] or ".png"
    baseline = os.path.join(baseline_dir, f"{name}{ext}")
    shutil.copy2(image_path, baseline)
    print(json.dumps({"action": "capture", "name": name, "baseline": baseline, "hash": file_hash(baseline)}))

def compare(name: str, image_path: str, threshold: float) -> None:
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    # Find baseline (try common extensions)
    baseline: str | None = None
    baseline_dir = baselines_dir()
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        candidate = os.path.join(baseline_dir, f"{name}{ext}")
        if os.path.exists(candidate):
            baseline = candidate
            break

    if not baseline:
        print(json.dumps({
            "action": "compare", "name": name, "error": "no baseline",
            "suggestion": f"Run: python3 snapshot-compare.py capture {name} {image_path}"
        }))
        sys.exit(1)

    # Try pixel-level diff first
    diff_pct = pixel_diff(baseline, image_path)
    method = "pixel"

    if diff_pct is None:
        # Fallback: hash comparison (exact match only)
        hash1 = file_hash(baseline)
        hash2 = file_hash(image_path)
        diff_pct = 0.0 if hash1 == hash2 else 100.0
        method = "hash"
        if diff_pct > 0:
            print("WARNING: Pillow not installed — using hash comparison (exact match only). "
                  "Install Pillow for pixel-level diff: pip install Pillow", file=sys.stderr)

    passed = diff_pct <= threshold

    result = {
        "action": "compare",
        "name": name,
        "baseline": baseline,
        "current": image_path,
        "diffPercent": diff_pct,
        "threshold": threshold,
        "method": method,
        "passed": passed,
    }
    print(json.dumps(result, indent=2))

    if not passed:
        print(f"VISUAL REGRESSION: {name} diff {diff_pct}% exceeds {threshold}% (method: {method})", file=sys.stderr)
        print(f"Update baseline: python3 snapshot-compare.py capture {name} {image_path}", file=sys.stderr)
        sys.exit(1)

def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    cap = sub.add_parser("capture")
    cap.add_argument("name")
    cap.add_argument("image_path")

    cmp = sub.add_parser("compare")
    cmp.add_argument("name")
    cmp.add_argument("image_path")
    cmp.add_argument("--threshold", type=float, default=5.0)

    args = parser.parse_args()
    if args.cmd == "capture":
        capture(args.name, args.image_path)
    elif args.cmd == "compare":
        compare(args.name, args.image_path, args.threshold)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
