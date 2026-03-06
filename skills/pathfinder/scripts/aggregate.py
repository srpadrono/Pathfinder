#!/usr/bin/env python3
"""Aggregate all pathfinder/journeys.json files in a project tree.

Usage: python3 aggregate.py [root-dir] [--output pathfinder/blazes.md]

Discovers all **/pathfinder/journeys.json files, merges them into a
combined summary, and optionally generates an aggregated blazes.md.
"""
import argparse, copy, json, os, re, sys, subprocess


def find_journey_files(root):
    """Find all pathfinder/journeys.json files in the tree."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden dirs and node_modules
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != 'node_modules']
        if os.path.basename(dirpath) == "pathfinder" and "journeys.json" in filenames:
            found.append(os.path.join(dirpath, "journeys.json"))
    return sorted(found)


def namespace_module_name(module_name):
    token = re.sub(r"[^A-Za-z0-9]+", "_", module_name).strip("_").upper()
    return token or "ROOT"


def namespace_journey(journey, module_name):
    prefix = namespace_module_name(module_name)
    namespaced = copy.deepcopy(journey)
    original_journey_id = namespaced.get("id", "JOURNEY")
    namespaced["_module"] = module_name
    namespaced["_sourceId"] = original_journey_id
    namespaced["id"] = f"{prefix}__{original_journey_id}"

    for step in namespaced.get("steps", []):
        original_step_id = step.get("id", "STEP")
        step["_sourceId"] = original_step_id
        step["id"] = f"{prefix}__{original_step_id}"

    return namespaced


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", help="Project root to scan")
    parser.add_argument("--output", default=None, help="Output aggregated blazes.md")
    parser.add_argument("--json", action="store_true", help="Output merged JSON to stdout")
    args = parser.parse_args()

    files = find_journey_files(args.root)

    if not files:
        print("No pathfinder/journeys.json files found.", file=sys.stderr)
        sys.exit(1)

    all_journeys = []
    modules = []

    for f in files:
        module_path = os.path.relpath(os.path.dirname(os.path.dirname(f)), args.root)  # e.g., e2e/tests from e2e/tests/pathfinder/journeys.json
        module_name = module_path or "root"

        with open(f) as fh:
            data = json.load(fh)

        journeys = data.get("journeys", [])
        total = sum(len(j.get("steps", [])) for j in journeys)
        tested = sum(sum(1 for s in j.get("steps", []) if s.get("tested") is True) for j in journeys)
        coverage = round(tested / total * 100, 1) if total else 0

        modules.append({
            "module": module_name,
            "file": f,
            "journeys": len(journeys),
            "steps": total,
            "tested": tested,
            "coverage": coverage,
        })

        # Prefix journey and step IDs with module name to avoid collisions.
        for j in journeys:
            all_journeys.append(namespace_journey(j, module_name))

    # Summary
    total_steps = sum(m["steps"] for m in modules)
    total_tested = sum(m["tested"] for m in modules)
    overall = round(total_tested / total_steps * 100, 1) if total_steps else 0

    result = {
        "modules": modules,
        "totalJourneys": len(all_journeys),
        "totalSteps": total_steps,
        "totalTested": total_tested,
        "overallCoverage": overall,
    }

    if args.json:
        # Output merged journeys
        merged = {"version": "1.0.0", "journeys": all_journeys}
        print(json.dumps(merged, indent=2))
    else:
        print(json.dumps(result, indent=2))

    # Print summary to stderr
    print(f"\nFound {len(files)} module(s):", file=sys.stderr)
    for m in modules:
        bar = "🟢" if m["coverage"] >= 80 else "🟡" if m["coverage"] >= 50 else "🔴"
        print(f"  {bar} {m['module']}: {m['tested']}/{m['steps']} ({m['coverage']}%)", file=sys.stderr)
    print(f"\n  Overall: {total_tested}/{total_steps} ({overall}%)", file=sys.stderr)

    # Generate aggregated blazes.md if requested
    if args.output:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gen_script = os.path.join(script_dir, "generate-diagrams.py")

        # Write merged journeys to temp file
        import tempfile
        merged = {"version": "1.0.0", "journeys": all_journeys}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(merged, tmp, indent=2)
            tmp_path = tmp.name

        subprocess.run(["python3", gen_script, tmp_path, "--output", args.output])
        os.unlink(tmp_path)


if __name__ == "__main__":
    main()
