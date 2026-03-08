#!/usr/bin/env python3
"""Tests for generate-diagrams.py"""
import json
import os
import subprocess
import tempfile

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
        r = subprocess.run(
            ["python3", SCRIPT, jpath, "--output",
             os.path.join(d, "out.md")],
            capture_output=True, text=True,
        )
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

def test_journey_missing_steps_field():
    """Journey dict without a 'steps' key should be rejected by validation."""
    with tempfile.TemporaryDirectory() as d:
        journeys = {
            "journeys": [{"id": "AUTH", "name": "Authentication"}]
        }
        jpath = os.path.join(d, "journeys.json")
        opath = os.path.join(d, "out.md")
        with open(jpath, "w") as f:
            json.dump(journeys, f)
        r = subprocess.run(["python3", SCRIPT, jpath, "--output", opath], capture_output=True, text=True)
        assert r.returncode == 1, "Should fail on journey missing 'steps'"
        assert "steps" in r.stderr.lower()
    print("pass: test_journey_missing_steps_field")


def test_journey_missing_id_field():
    """Journey dict without an 'id' key should be rejected by validation."""
    with tempfile.TemporaryDirectory() as d:
        journeys = {
            "journeys": [{"name": "No ID Journey", "steps": [
                {"id": "X-01", "action": "Step one", "screen": "/main", "tested": True},
            ]}]
        }
        jpath = os.path.join(d, "journeys.json")
        opath = os.path.join(d, "out.md")
        with open(jpath, "w") as f:
            json.dump(journeys, f)
        r = subprocess.run(["python3", SCRIPT, jpath, "--output", opath], capture_output=True, text=True)
        assert r.returncode == 1, "Should fail on journey missing 'id'"
        assert "id" in r.stderr.lower()
    print("pass: test_journey_missing_id_field")


def test_step_missing_tested_field():
    """Step without 'tested' field should be rejected by validation."""
    with tempfile.TemporaryDirectory() as d:
        journeys = {
            "journeys": [{"id": "AUTH", "name": "Auth", "steps": [
                {"id": "AUTH-01", "action": "Login", "screen": "/login"},
            ]}]
        }
        jpath = os.path.join(d, "journeys.json")
        opath = os.path.join(d, "out.md")
        with open(jpath, "w") as f:
            json.dump(journeys, f)
        r = subprocess.run(["python3", SCRIPT, jpath, "--output", opath], capture_output=True, text=True)
        assert r.returncode == 1, "Should fail on step missing 'tested'"
        assert "tested" in r.stderr.lower()
    print("pass: test_step_missing_tested_field")


def test_tested_as_string_instead_of_boolean():
    """tested='true' (string) should be rejected by validation."""
    with tempfile.TemporaryDirectory() as d:
        journeys = {
            "journeys": [{"id": "AUTH", "name": "Auth", "steps": [
                {"id": "AUTH-01", "action": "Login", "screen": "/login", "tested": "true"},
            ]}]
        }
        jpath = os.path.join(d, "journeys.json")
        opath = os.path.join(d, "out.md")
        with open(jpath, "w") as f:
            json.dump(journeys, f)
        r = subprocess.run(["python3", SCRIPT, jpath, "--output", opath], capture_output=True, text=True)
        assert r.returncode == 1, "Should fail on tested='true' (string instead of boolean)"
        assert "tested" in r.stderr.lower()
    print("pass: test_tested_as_string_instead_of_boolean")


def test_journey_with_zero_steps():
    """Journey with an empty steps array should not crash."""
    with tempfile.TemporaryDirectory() as d:
        journeys = {
            "journeys": [
                {"id": "EMPTY", "name": "Empty Journey", "steps": []},
                {"id": "REAL", "name": "Real Journey", "steps": [
                    {"id": "R-01", "action": "Do thing", "screen": "/main", "tested": True},
                ]},
            ]
        }
        jpath = os.path.join(d, "journeys.json")
        opath = os.path.join(d, "out.md")
        with open(jpath, "w") as f:
            json.dump(journeys, f)
        r = subprocess.run(["python3", SCRIPT, jpath, "--output", opath], capture_output=True, text=True)
        assert r.returncode == 0, f"Failed: {r.stderr}"
        content = open(opath).read()
        assert "Real Journey" in content
    print("pass: test_journey_with_zero_steps")


def test_shared_step_ids_create_decision_nodes():
    """Journeys sharing step IDs at branching points produce diamond decision nodes."""
    with tempfile.TemporaryDirectory() as d:
        journeys = {
            "journeys": [
                {"id": "ITEMS-LIST", "name": "Items List", "steps": [
                    {"id": "ITEMS-01", "action": "User sees items list", "screen": "ItemsListView", "tested": True},
                    {"id": "ITEMS-02", "action": "User searches items", "screen": "ItemsListView", "tested": True},
                ]},
                {"id": "ITEMS-CREATE", "name": "Create Item", "steps": [
                    {"id": "ITEMS-01", "action": "User sees items list", "screen": "ItemsListView", "tested": True},
                    {"id": "ICREATE-01", "action": "User taps add button", "screen": "ItemsListView", "tested": False},
                    {"id": "ICREATE-02", "action": "User fills form", "screen": "ItemFormView", "tested": False},
                ]},
                {"id": "ITEMS-DELETE", "name": "Delete Item", "steps": [
                    {"id": "ITEMS-01", "action": "User sees items list", "screen": "ItemsListView", "tested": True},
                    {"id": "IDEL-01", "action": "User swipes to delete", "screen": "ItemsListView", "tested": False},
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
        # ITEMS_01 should have a decision diamond because it has 3 children
        assert "ITEMS_01_decision" in decision_tree, f"Missing decision node in:\n{decision_tree}"
        assert "🔀 User action?" in decision_tree, f"Missing decision label in:\n{decision_tree}"
    print("✅ test_shared_step_ids_create_decision_nodes")


def test_shared_steps_deduplicated_in_coverage():
    """Overall coverage deduplicates shared step IDs to avoid inflated counts."""
    with tempfile.TemporaryDirectory() as d:
        journeys = {
            "journeys": [
                {"id": "A", "name": "Flow A", "steps": [
                    {"id": "SHARED-01", "action": "Start", "screen": "/", "tested": True},
                    {"id": "A-01", "action": "Step A", "screen": "/a", "tested": False},
                ]},
                {"id": "B", "name": "Flow B", "steps": [
                    {"id": "SHARED-01", "action": "Start", "screen": "/", "tested": True},
                    {"id": "B-01", "action": "Step B", "screen": "/b", "tested": True},
                ]},
            ]
        }
        jpath = os.path.join(d, "journeys.json")
        opath = os.path.join(d, "out.md")
        with open(jpath, "w") as f:
            json.dump(journeys, f)

        r = subprocess.run(["python3", SCRIPT, jpath, "--output", opath], capture_output=True, text=True)
        assert r.returncode == 0, f"Failed: {r.stderr}"
        content = open(opath).read()
        # 3 unique steps: SHARED-01 (tested), A-01 (not), B-01 (tested)
        # Overall = 2/3 = 66.7%
        assert "66.7%" in content, f"Expected 66.7% overall coverage in:\n{content}"
        # Per-journey: Flow A = 1/2 = 50%, Flow B = 2/2 = 100%
        assert "50.0%" in content, f"Expected 50.0% per-journey coverage in:\n{content}"
        assert "100.0%" in content, f"Expected 100.0% per-journey coverage in:\n{content}"
    print("✅ test_shared_steps_deduplicated_in_coverage")


if __name__ == "__main__":
    test_basic_diagram()
    test_empty_journeys()
    test_all_tested()
    test_decision_tree_keeps_independent_roots()
    test_output_filename_without_directory()
    test_error_journey_attaches_to_loading_step()
    test_journey_missing_steps_field()
    test_journey_missing_id_field()
    test_step_missing_tested_field()
    test_tested_as_string_instead_of_boolean()
    test_journey_with_zero_steps()
    test_shared_step_ids_create_decision_nodes()
    test_shared_steps_deduplicated_in_coverage()
    print("\nAll generate-diagrams tests passed")
