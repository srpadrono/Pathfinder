#!/usr/bin/env python3
"""Run skill evals for the Pathfinder skill.

Executes each eval case from evals.json, sets up fixture files in a temporary
workspace, runs the relevant Pathfinder scripts, and captures outputs for
grading.

Usage:
    python run_evals.py [--iteration N] [--eval-id ID] [--dry-run]

Options:
    --iteration N   Iteration number (default: 1). Creates iteration-N/ dir.
    --eval-id ID    Run only a specific eval by ID.
    --dry-run       Print what would run without executing.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent.parent  # pathfinder-workspace/evals/
WORKSPACE = EVALS_DIR.parent  # pathfinder-workspace/
EVALS_JSON = EVALS_DIR / "evals.json"
SKILL_SCRIPTS = Path(__file__).resolve().parents[3] / "skills" / "pathfinder" / "scripts"

# Map eval names to the primary script they exercise
SCRIPT_MAP = {
    "nextjs-playwright-map-and-blaze": ["detect-ui-framework.py", "scan-test-coverage.py", "generate-diagrams.py"],
    "ios-xcuitest-coverage": ["detect-ui-framework.py", "scan-test-coverage.py"],
    "baseline-comparison-diagrams": ["generate-diagrams.py"],
    "monorepo-aggregation": ["pathfinder-init.py", "detect-ui-framework.py", "aggregate.py"],
    "scout-without-remap": ["generate-ui-test.py"],
    "flutter-zero-tests": ["detect-ui-framework.py", "scan-test-coverage.py"],
    "multi-framework-conflict": ["detect-ui-framework.py"],
    "malformed-json-blaze-error": ["generate-diagrams.py"],
    "malformed-json-map-error": ["validate-journeys.py"],
    "empty-project-no-journeys": ["scan-test-coverage.py"],
    "scout-missing-journeys": ["generate-ui-test.py"],
}


def load_evals() -> dict:
    with open(EVALS_JSON) as f:
        return json.load(f)


def setup_fixture_dir(eval_case: dict, iteration_dir: Path) -> Path:
    """Copy fixture files into a temporary eval directory."""
    eval_name = eval_case.get("name", f"eval-{eval_case['id']}")
    eval_dir = iteration_dir / f"eval-{eval_case['id']}-{eval_name}"
    with_skill = eval_dir / "with_skill"
    outputs = with_skill / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)

    fixture_dst = with_skill / "fixtures"
    fixture_dst.mkdir(parents=True, exist_ok=True)

    for rel_path in eval_case.get("files", []):
        src = EVALS_DIR / rel_path
        dst = fixture_dst / Path(rel_path).name
        if src.exists():
            shutil.copy2(src, dst)

    # Write eval metadata
    metadata = {
        "eval_id": eval_case["id"],
        "eval_name": eval_name,
        "prompt": eval_case["prompt"],
        "assertions": eval_case.get("assertions", []),
    }
    with open(eval_dir / "eval_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return eval_dir


def run_scripts_for_eval(eval_case: dict, eval_dir: Path, dry_run: bool = False) -> dict:
    """Run the relevant Pathfinder scripts for a given eval case."""
    eval_name = eval_case.get("name", f"eval-{eval_case['id']}")
    scripts = SCRIPT_MAP.get(eval_name, [])
    with_skill = eval_dir / "with_skill"
    outputs_dir = with_skill / "outputs"
    fixture_dir = with_skill / "fixtures"

    results = {
        "eval_id": eval_case["id"],
        "eval_name": eval_name,
        "scripts_run": [],
        "outputs": [],
        "errors": [],
        "exit_codes": [],
    }

    if dry_run:
        print(f"  [DRY RUN] Would run scripts: {scripts}")
        results["scripts_run"] = scripts
        return results

    for script_name in scripts:
        script_path = SKILL_SCRIPTS / script_name
        if not script_path.exists():
            results["errors"].append(f"Script not found: {script_path}")
            continue

        cmd = [sys.executable, str(script_path)]

        # Add appropriate arguments based on the script
        if script_name == "detect-ui-framework.py":
            cmd.append(str(fixture_dir))
        elif script_name == "scan-test-coverage.py":
            cmd.append(str(fixture_dir))
        elif script_name == "generate-diagrams.py":
            # Find journeys.json in fixtures
            journeys_file = fixture_dir / "journeys-existing.json"
            if not journeys_file.exists():
                # Check for malformed version
                journeys_file = fixture_dir / "malformed-journeys.json"
            if journeys_file.exists():
                cmd.append(str(journeys_file))
            else:
                cmd.append(str(fixture_dir / "journeys.json"))
        elif script_name == "validate-journeys.py":
            journeys_file = fixture_dir / "malformed-journeys.json"
            if not journeys_file.exists():
                journeys_file = fixture_dir / "journeys-existing.json"
            cmd.append(str(journeys_file))
        elif script_name == "aggregate.py":
            cmd.append(str(fixture_dir))
        elif script_name == "generate-ui-test.py":
            # Needs journey ID, description, and framework
            cmd.extend(["s3", "test untested step", "playwright", "--auto"])
        elif script_name == "pathfinder-init.py":
            cmd.extend(["--output-dir", str(outputs_dir)])

        start_time = time.time()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(fixture_dir),
            )
            duration_ms = int((time.time() - start_time) * 1000)

            results["scripts_run"].append(script_name)
            results["exit_codes"].append(proc.returncode)

            output_data = {
                "script": script_name,
                "exit_code": proc.returncode,
                "stdout": proc.stdout[:5000],  # Truncate long output
                "stderr": proc.stderr[:2000],
                "duration_ms": duration_ms,
            }
            results["outputs"].append(output_data)

            # Save individual script output
            output_file = outputs_dir / f"{Path(script_name).stem}-output.json"
            with open(output_file, "w") as f:
                json.dump(output_data, f, indent=2)

        except subprocess.TimeoutExpired:
            results["errors"].append(f"Timeout running {script_name}")
            results["exit_codes"].append(-1)
        except Exception as e:
            results["errors"].append(f"Error running {script_name}: {e}")
            results["exit_codes"].append(-1)

    return results


def run_eval(eval_case: dict, iteration_dir: Path, dry_run: bool = False) -> dict:
    """Run a single eval case end-to-end."""
    eval_name = eval_case.get("name", f"eval-{eval_case['id']}")
    print(f"\n{'='*60}")
    print(f"Eval {eval_case['id']}: {eval_name}")
    print(f"Prompt: {eval_case['prompt'][:80]}...")
    print(f"{'='*60}")

    eval_dir = setup_fixture_dir(eval_case, iteration_dir)
    start_time = time.time()
    results = run_scripts_for_eval(eval_case, eval_dir, dry_run)
    total_duration = int((time.time() - start_time) * 1000)

    # Save timing data
    timing = {
        "total_duration_ms": total_duration,
        "total_duration_seconds": round(total_duration / 1000, 2),
        "scripts_run": len(results["scripts_run"]),
    }
    timing_file = eval_dir / "with_skill" / "timing.json"
    with open(timing_file, "w") as f:
        json.dump(timing, f, indent=2)

    # Save combined results
    results_file = eval_dir / "with_skill" / "results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    passed_scripts = sum(1 for c in results["exit_codes"] if c == 0)
    total_scripts = len(results["exit_codes"])
    print(f"  Scripts: {passed_scripts}/{total_scripts} succeeded")
    if results["errors"]:
        for err in results["errors"]:
            print(f"  Error: {err}")
    print(f"  Duration: {total_duration}ms")

    return results


def main():
    parser = argparse.ArgumentParser(description="Run Pathfinder skill evals")
    parser.add_argument("--iteration", type=int, default=1, help="Iteration number")
    parser.add_argument("--eval-id", type=int, default=None, help="Run specific eval ID")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without executing")
    args = parser.parse_args()

    data = load_evals()
    evals = data["evals"]

    if args.eval_id is not None:
        evals = [e for e in evals if e["id"] == args.eval_id]
        if not evals:
            print(f"Error: No eval found with id {args.eval_id}", file=sys.stderr)
            sys.exit(1)

    iteration_dir = WORKSPACE / f"iteration-{args.iteration}"
    iteration_dir.mkdir(parents=True, exist_ok=True)

    print("Pathfinder Skill Eval Runner")
    print(f"Iteration: {args.iteration}")
    print(f"Evals to run: {len(evals)}")
    print(f"Output: {iteration_dir}")
    if args.dry_run:
        print("[DRY RUN MODE]")

    all_results = []
    start_time = time.time()

    for eval_case in evals:
        result = run_eval(eval_case, iteration_dir, args.dry_run)
        all_results.append(result)

    total_time = round(time.time() - start_time, 2)

    # Save summary
    summary = {
        "iteration": args.iteration,
        "total_evals": len(all_results),
        "total_duration_seconds": total_time,
        "results": all_results,
    }
    summary_file = iteration_dir / "run_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Run complete: {len(all_results)} evals in {total_time}s")
    print(f"Summary: {summary_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
