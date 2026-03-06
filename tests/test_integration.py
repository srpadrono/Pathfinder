#!/usr/bin/env python3
"""Integration test: exercises the full Pathfinder flow end-to-end.

1. Create a temp directory with mock source files
2. Run pathfinder-init.py
3. Create a minimal journeys.json
4. Run generate-diagrams.py on it
5. Run coverage-score.py on it
6. Verify outputs are valid JSON and diagrams are valid Mermaid
"""
import json
import os
import re
import subprocess
import tempfile

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills", "pathfinder", "scripts")
INIT_SCRIPT = os.path.join(SCRIPTS_DIR, "pathfinder-init.py")
DIAGRAMS_SCRIPT = os.path.join(SCRIPTS_DIR, "generate-diagrams.py")
COVERAGE_SCRIPT = os.path.join(SCRIPTS_DIR, "coverage-score.py")


def test_full_flow():
    """Run init -> create journeys -> generate diagrams -> coverage score."""
    with tempfile.TemporaryDirectory() as d:
        # Step 1: Create mock source files to simulate a web project
        tests_dir = os.path.join(d, "tests")
        os.makedirs(tests_dir)
        # Create a playwright config so detect-ui-framework finds something
        with open(os.path.join(d, "playwright.config.ts"), "w") as f:
            f.write("export default { testDir: './tests' };\n")
        with open(os.path.join(d, "package.json"), "w") as f:
            json.dump({"name": "integration-test", "devDependencies": {"@playwright/test": "^1.0"}}, f)

        # Step 2: Run pathfinder-init.py
        r = subprocess.run(
            ["python3", INIT_SCRIPT, "--name", "integration-test"],
            cwd=d,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"Init failed: {r.stderr}\n{r.stdout}"

        # Find the pathfinder directory that was created
        pathfinder_dir = None
        for root, _dirs, files in os.walk(d):
            if os.path.basename(root) == "pathfinder" and "config.json" in files:
                pathfinder_dir = root
                break
        assert pathfinder_dir is not None, "pathfinder-init should create a pathfinder/ directory"

        # Verify config.json is valid JSON
        config_path = os.path.join(pathfinder_dir, "config.json")
        assert os.path.exists(config_path), "config.json should exist"
        with open(config_path) as f:
            config = json.load(f)
        assert config["project"] == "integration-test"
        assert "framework" in config

        # Step 3: Create a minimal journeys.json
        journeys_data = {
            "version": "1.0.0",
            "project": "integration-test",
            "framework": config.get("framework", "playwright"),
            "journeys": [
                {
                    "id": "AUTH",
                    "name": "Authentication",
                    "steps": [
                        {"id": "AUTH-01", "action": "Open login page", "screen": "/login", "tested": True},
                        {"id": "AUTH-02", "action": "Enter credentials", "screen": "/login", "tested": True},
                        {"id": "AUTH-03", "action": "See dashboard", "screen": "/dashboard", "tested": False},
                    ]
                },
                {
                    "id": "NAV",
                    "name": "Navigation",
                    "steps": [
                        {"id": "NAV-01", "action": "Click settings", "screen": "/dashboard", "tested": False},
                        {"id": "NAV-02", "action": "See settings page", "screen": "/settings", "tested": False},
                    ]
                },
            ]
        }
        journeys_path = os.path.join(pathfinder_dir, "journeys.json")
        with open(journeys_path, "w") as f:
            json.dump(journeys_data, f, indent=2)

        # Step 4: Run generate-diagrams.py
        blazes_path = os.path.join(pathfinder_dir, "blazes.md")
        r = subprocess.run(
            ["python3", DIAGRAMS_SCRIPT, journeys_path, "--output", blazes_path],
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"Generate diagrams failed: {r.stderr}"
        assert os.path.exists(blazes_path), "blazes.md should be created"

        # Verify the output contains valid Mermaid blocks
        with open(blazes_path) as f:
            diagrams_content = f.read()

        # Check for Mermaid code blocks
        mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", diagrams_content, re.DOTALL)
        assert len(mermaid_blocks) >= 1, "Should contain at least one mermaid block"

        # Verify each Mermaid block starts with a valid directive
        for block in mermaid_blocks:
            stripped = block.strip()
            assert stripped.startswith("flowchart"), f"Mermaid block should start with 'flowchart': {stripped[:50]}"

        # Verify coverage numbers appear
        assert "Authentication" in diagrams_content
        assert "Navigation" in diagrams_content

        # The last line of stdout should be valid JSON summary
        stdout_lines = r.stdout.strip().split("\n")
        summary_json = json.loads(stdout_lines[-1])
        assert summary_json["totalSteps"] == 5
        assert summary_json["tested"] == 2
        assert summary_json["journeys"] == 2
        assert summary_json["coverage"] == 40.0

        # Step 5: Run coverage-score.py
        r = subprocess.run(
            ["python3", COVERAGE_SCRIPT, journeys_path],
            capture_output=True,
            text=True,
        )
        # 40% coverage is below 50% threshold, so exit code should be 1
        assert r.returncode == 1, f"Expected exit 1 for low coverage, got {r.returncode}"

        # Verify coverage output is valid JSON
        coverage = json.loads(r.stdout)
        assert coverage["totalSteps"] == 5
        assert coverage["tested"] == 2
        assert coverage["coverage"] == 40.0
        assert coverage["untested"] == 3
        assert len(coverage["journeys"]) == 2

        # Per-journey coverage
        auth_journey = next(j for j in coverage["journeys"] if j["id"] == "AUTH")
        assert auth_journey["coverage"] == 66.7
        assert auth_journey["tested"] == 2

        nav_journey = next(j for j in coverage["journeys"] if j["id"] == "NAV")
        assert nav_journey["coverage"] == 0.0
        assert nav_journey["tested"] == 0

    print("pass: test_full_flow")


def test_full_flow_high_coverage():
    """Full flow with high coverage should produce exit 0 from coverage-score."""
    with tempfile.TemporaryDirectory() as d:
        pdir = os.path.join(d, "tests", "pathfinder")
        os.makedirs(pdir)

        journeys_data = {
            "version": "1.0.0",
            "project": "good-project",
            "journeys": [
                {
                    "id": "FLOW",
                    "name": "Main Flow",
                    "steps": [
                        {"id": "FLOW-01", "action": "Step 1", "screen": "/main", "tested": True},
                        {"id": "FLOW-02", "action": "Step 2", "screen": "/main", "tested": True},
                        {"id": "FLOW-03", "action": "Step 3", "screen": "/done", "tested": True},
                    ]
                }
            ]
        }
        journeys_path = os.path.join(pdir, "journeys.json")
        with open(journeys_path, "w") as f:
            json.dump(journeys_data, f, indent=2)

        # Generate diagrams
        blazes_path = os.path.join(pdir, "blazes.md")
        r = subprocess.run(
            ["python3", DIAGRAMS_SCRIPT, journeys_path, "--output", blazes_path],
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"Generate diagrams failed: {r.stderr}"

        # Verify mermaid content
        with open(blazes_path) as f:
            content = f.read()
        assert "100.0%" in content

        # Coverage score should pass (100% >= 50%)
        r = subprocess.run(
            ["python3", COVERAGE_SCRIPT, journeys_path],
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"Expected exit 0 for high coverage, got {r.returncode}"
        coverage = json.loads(r.stdout)
        assert coverage["coverage"] == 100.0

    print("pass: test_full_flow_high_coverage")


if __name__ == "__main__":
    test_full_flow()
    test_full_flow_high_coverage()
    print("\nAll integration tests passed")
