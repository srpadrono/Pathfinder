#!/usr/bin/env python3
"""Tests for generate-diagrams.py"""
import subprocess, json, tempfile, os

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "skills", "pathfinder", "scripts", "generate-diagrams.py")

def test_basic_diagram():
    with tempfile.TemporaryDirectory() as d:
        journeys = {
            "version": "1.0.0", "project": "test",
            "journeys": [{
                "id": "AUTH", "name": "Authentication",
                "steps": [
                    {"id": "AUTH-01", "action": "Login", "screen": "/login", "tested": True},
                    {"id": "AUTH-02", "action": "See dashboard", "screen": "/dash", "tested": False},
                ]
            }]
        }
        jpath = os.path.join(d, "journeys.json")
        opath = os.path.join(d, "diagrams.md")
        with open(jpath, "w") as f:
            json.dump(journeys, f)

        r = subprocess.run(["python3", SCRIPT, jpath, "--output", opath], capture_output=True, text=True)
        assert r.returncode == 0, f"Failed: {r.stderr}"

        with open(opath) as f:
            content = f.read()

        assert "✅" in content, "Missing ✅ marker"
        assert "❌" in content, "Missing ❌ marker"
        assert "50.0%" in content, f"Wrong coverage in: {content}"
        assert "🔐" in content, "Missing auth icon"
        assert "```mermaid" in content, "Missing mermaid block"
    print("✅ test_basic_diagram")

def test_empty_journeys():
    with tempfile.TemporaryDirectory() as d:
        jpath = os.path.join(d, "journeys.json")
        with open(jpath, "w") as f:
            json.dump({"journeys": []}, f)
        r = subprocess.run(["python3", SCRIPT, jpath, "--output", os.path.join(d, "out.md")], capture_output=True, text=True)
        assert r.returncode == 1, "Should fail on empty journeys"
    print("✅ test_empty_journeys")

def test_all_tested():
    with tempfile.TemporaryDirectory() as d:
        journeys = {
            "journeys": [{"id": "X", "name": "Flow", "steps": [
                {"id": "X-01", "action": "Step", "screen": "/", "tested": True},
            ]}]
        }
        jpath = os.path.join(d, "journeys.json")
        opath = os.path.join(d, "out.md")
        with open(jpath, "w") as f:
            json.dump(journeys, f)
        r = subprocess.run(["python3", SCRIPT, jpath, "--output", opath], capture_output=True, text=True)
        assert r.returncode == 0
        assert "100.0%" in open(opath).read()
    print("✅ test_all_tested")

if __name__ == "__main__":
    test_basic_diagram()
    test_empty_journeys()
    test_all_tested()
    print("\nAll generate-diagrams tests passed")
