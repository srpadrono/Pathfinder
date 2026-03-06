#!/usr/bin/env python3
"""Tests for generate-diagrams.py"""
import subprocess, json, tempfile, os

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "skills", "pathfinder", "scripts", "generate-diagrams.py")


def _decision_tree_section(content):
    marker = "## 🌳 Decision Tree — All Paths\n"
    assert marker in content, content
    section = content.split(marker, 1)[1]
    return section.split("\n## ", 1)[0]

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


def test_decision_tree_keeps_independent_roots():
    with tempfile.TemporaryDirectory() as d:
        journeys = {
            "journeys": [
                {"id": "AUTH", "name": "Auth", "steps": [
                    {"id": "AUTH-01", "action": "Open login", "screen": "/login", "tested": True},
                    {"id": "AUTH-02", "action": "Submit", "screen": "/login", "tested": False},
                ]},
                {"id": "SETTINGS", "name": "Settings", "steps": [
                    {"id": "SET-01", "action": "Open settings", "screen": "/settings", "tested": True},
                    {"id": "SET-02", "action": "Save", "screen": "/settings", "tested": False},
                ]},
            ]
        }
        jpath = os.path.join(d, "journeys.json")
        opath = os.path.join(d, "out.md")
        with open(jpath, "w") as f:
            json.dump(journeys, f)

        r = subprocess.run(["python3", SCRIPT, jpath, "--output", opath], capture_output=True, text=True)
        assert r.returncode == 0, f"Failed: {r.stderr}"
        decision_tree = _decision_tree_section(open(opath).read())
        assert "Open login" in decision_tree
        assert "Open settings" in decision_tree, decision_tree
    print("✅ test_decision_tree_keeps_independent_roots")


def test_output_filename_without_directory():
    with tempfile.TemporaryDirectory() as d:
        journeys = {
            "journeys": [{"id": "AUTH", "name": "Auth", "steps": [
                {"id": "AUTH-01", "action": "Login", "screen": "/login", "tested": True},
            ]}]
        }
        jpath = os.path.join(d, "journeys.json")
        with open(jpath, "w") as f:
            json.dump(journeys, f)

        r = subprocess.run(
            ["python3", SCRIPT, "journeys.json", "--output", "blazes.md"],
            cwd=d,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"Failed: {r.stderr}"
        assert os.path.exists(os.path.join(d, "blazes.md"))
    print("✅ test_output_filename_without_directory")


def test_error_journey_attaches_to_loading_step():
    with tempfile.TemporaryDirectory() as d:
        journeys = {
            "journeys": [
                {"id": "CHECKOUT", "name": "Checkout", "steps": [
                    {"id": "CHECKOUT-01", "action": "Open checkout", "screen": "/checkout", "tested": True},
                    {"id": "CHECKOUT-02", "action": "Payment loading", "screen": "/checkout", "tested": True},
                    {"id": "CHECKOUT-03", "action": "Order confirmed", "screen": "/confirmation", "tested": False},
                ]},
                {"id": "ERROR", "name": "Checkout Error", "steps": [
                    {"id": "ERROR-01", "action": "Card declined", "screen": "/checkout", "tested": False},
                    {"id": "ERROR-02", "action": "Retry payment", "screen": "/checkout", "tested": False},
                ]},
            ]
        }
        jpath = os.path.join(d, "journeys.json")
        opath = os.path.join(d, "out.md")
        with open(jpath, "w") as f:
            json.dump(journeys, f)

        r = subprocess.run(["python3", SCRIPT, jpath, "--output", opath], capture_output=True, text=True)
        assert r.returncode == 0, f"Failed: {r.stderr}"
        decision_tree = _decision_tree_section(open(opath).read())
        assert 'CHECKOUT_02 -.->|"⚡ API Error"| ERROR_01' in decision_tree, decision_tree
    print("✅ test_error_journey_attaches_to_loading_step")

if __name__ == "__main__":
    test_basic_diagram()
    test_empty_journeys()
    test_all_tested()
    test_decision_tree_keeps_independent_roots()
    test_output_filename_without_directory()
    test_error_journey_attaches_to_loading_step()
    print("\nAll generate-diagrams tests passed")
