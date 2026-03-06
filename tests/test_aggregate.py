#!/usr/bin/env python3
"""Tests for aggregate.py"""
import json
import os
import subprocess
import tempfile

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "skills", "pathfinder", "scripts", "aggregate.py")


def test_discover_modules():
    """Should find pathfinder/journeys.json in subdirectories."""
    with tempfile.TemporaryDirectory() as d:
        # Create two modules
        for mod in ["auth", "reports"]:
            pdir = os.path.join(d, "modules", mod, "tests", "pathfinder")
            os.makedirs(pdir)
            data = {"journeys": [{"id": f"{mod.upper()}-01", "name": f"{mod} journey",
                     "steps": [{"id": f"{mod}-1", "tested": True}, {"id": f"{mod}-2", "tested": False}]}]}
            with open(os.path.join(pdir, "journeys.json"), "w") as f:
                json.dump(data, f)

        r = subprocess.run(["python3", SCRIPT, d], capture_output=True, text=True)
        assert r.returncode == 0, f"Failed: {r.stderr}"
        result = json.loads(r.stdout)
        assert len(result["modules"]) == 2
        assert result["totalSteps"] == 4
        assert result["totalTested"] == 2
        assert result["overallCoverage"] == 50.0
        print("✅ test_discover_modules passed")


def test_no_modules():
    """Should exit 1 when no journeys found."""
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(["python3", SCRIPT, d], capture_output=True, text=True)
        assert r.returncode == 1
        print("✅ test_no_modules passed")


def test_json_output():
    """--json should output merged journeys."""
    with tempfile.TemporaryDirectory() as d:
        pdir = os.path.join(d, "tests", "pathfinder")
        os.makedirs(pdir)
        data = {"journeys": [{"id": "A-01", "name": "Auth", "steps": [{"id": "a1", "tested": True}]}]}
        with open(os.path.join(pdir, "journeys.json"), "w") as f:
            json.dump(data, f)

        r = subprocess.run(["python3", SCRIPT, d, "--json"], capture_output=True, text=True)
        assert r.returncode == 0
        merged = json.loads(r.stdout)
        assert len(merged["journeys"]) == 1
        assert merged["journeys"][0]["_module"] == "tests"
        print("✅ test_json_output passed")


def test_namespaces_duplicate_ids_in_aggregate_output():
    """Should preserve both modules when IDs overlap."""
    with tempfile.TemporaryDirectory() as d:
        fixtures = {
            "app1": {"id": "AUTH", "name": "Auth A", "steps": [
                {"id": "AUTH-01", "action": "Open A", "screen": "/a", "tested": True},
                {"id": "AUTH-02", "action": "Done A", "screen": "/a", "tested": False},
            ]},
            "app2": {"id": "AUTH", "name": "Auth B", "steps": [
                {"id": "AUTH-01", "action": "Open B", "screen": "/b", "tested": True},
                {"id": "AUTH-02", "action": "Done B", "screen": "/b", "tested": False},
            ]},
        }

        for module, journey in fixtures.items():
            pdir = os.path.join(d, module, "e2e", "tests", "pathfinder")
            os.makedirs(pdir)
            with open(os.path.join(pdir, "journeys.json"), "w") as f:
                json.dump({"journeys": [journey]}, f)

        md_path = os.path.join(d, "blazes.md")
        r = subprocess.run(["python3", SCRIPT, d, "--output", md_path], capture_output=True, text=True)
        assert r.returncode == 0, f"Failed: {r.stderr}"

        diagrams = open(md_path).read()
        # Extract decision tree section more robustly using marker + next section boundary
        marker = "## 🌳 Decision Tree — All Paths\n"
        assert marker in diagrams, "Expected decision tree section in output"
        after_marker = diagrams.split(marker, 1)[1]
        # Find the next section header (## ) or end of file
        import re as _re
        next_section = _re.search(r"\n## ", after_marker)
        decision_tree = after_marker[:next_section.start()] if next_section else after_marker
        assert "Open A" in decision_tree
        assert "Open B" in decision_tree, decision_tree

        r_json = subprocess.run(["python3", SCRIPT, d, "--json"], capture_output=True, text=True)
        assert r_json.returncode == 0, f"JSON failed: {r_json.stderr}"
        merged = json.loads(r_json.stdout)
        journey_ids = [journey["id"] for journey in merged["journeys"]]
        step_ids = [step["id"] for journey in merged["journeys"] for step in journey["steps"]]
        assert len(set(journey_ids)) == len(journey_ids), journey_ids
        assert len(set(step_ids)) == len(step_ids), step_ids
        print("✅ test_namespaces_duplicate_ids_in_aggregate_output passed")


if __name__ == "__main__":
    test_discover_modules()
    test_no_modules()
    test_json_output()
    test_namespaces_duplicate_ids_in_aggregate_output()
    print("\nAll aggregate tests passed")
