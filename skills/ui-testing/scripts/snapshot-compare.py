#!/usr/bin/env python3
"""Visual regression: capture and compare screenshots.

Usage:
  python3 snapshot-compare.py capture <name> <image-path>
  python3 snapshot-compare.py compare <name> <image-path> [--threshold 5]

Baselines stored in .pathfinder/baselines/
"""
import argparse, os, sys, json, shutil

BASELINES_DIR = ".pathfinder/baselines"

def capture(name, image_path):
    os.makedirs(BASELINES_DIR, exist_ok=True)
    ext = os.path.splitext(image_path)[1] or ".png"
    baseline = os.path.join(BASELINES_DIR, f"{name}{ext}")
    shutil.copy2(image_path, baseline)
    print(json.dumps({"action": "capture", "name": name, "baseline": baseline}))

def compare(name, image_path, threshold):
    ext = os.path.splitext(image_path)[1] or ".png"
    baseline = os.path.join(BASELINES_DIR, f"{name}{ext}")

    if not os.path.exists(baseline):
        print(json.dumps({"action": "compare", "name": name, "error": "no baseline", "suggestion": f"Run: python3 snapshot-compare.py capture {name} {image_path}"}))
        sys.exit(1)

    # Simple file size comparison as proxy (real pixel diff needs PIL/Pillow)
    baseline_size = os.path.getsize(baseline)
    current_size = os.path.getsize(image_path)

    if baseline_size == 0:
        diff_pct = 100.0
    else:
        diff_pct = abs(current_size - baseline_size) / baseline_size * 100

    passed = diff_pct <= threshold

    result = {
        "action": "compare",
        "name": name,
        "baseline": baseline,
        "current": image_path,
        "diffPercent": round(diff_pct, 2),
        "threshold": threshold,
        "passed": passed,
    }
    print(json.dumps(result, indent=2))

    if not passed:
        print(f"VISUAL REGRESSION: {name} diff {diff_pct:.1f}% exceeds {threshold}%", file=sys.stderr)
        print(f"Update baseline: python3 snapshot-compare.py capture {name} {image_path}", file=sys.stderr)
        sys.exit(1)

def main():
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
