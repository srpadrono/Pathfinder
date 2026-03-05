#!/usr/bin/env python3
"""Tests for aggregate.py"""
import subprocess, json, tempfile, os

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "skill", "scripts", "aggregate.py")


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


if __name__ == "__main__":
    test_discover_modules()
    test_no_modules()
    test_json_output()
    print("\nAll aggregate tests passed")
