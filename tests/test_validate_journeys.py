#!/usr/bin/env python3
"""Tests for validate-journeys.py"""
import subprocess, json, tempfile, os

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "skill", "scripts", "validate-journeys.py")


def run(filepath):
    r = subprocess.run(["python3", SCRIPT, filepath], capture_output=True, text=True)
    return r.returncode, json.loads(r.stdout) if r.stdout.strip() else {}


def write_json(tmpdir, data):
    path = os.path.join(tmpdir, "journeys.json")
    with open(path, "w") as f:
        json.dump(data, f)
    return path


def test_valid_journeys():
    with tempfile.TemporaryDirectory() as d:
        path = write_json(d, {
            "version": "1.0",
            "project": "demo",
            "framework": "playwright",
            "journeys": [
                {
                    "id": "auth",
                    "name": "Authentication",
                    "steps": [
                        {"id": "AUTH-01", "action": "click login", "screen": "login", "tested": True},
                        {"id": "AUTH-02", "action": "enter password", "screen": "login", "tested": False},
                    ]
                }
            ]
        })
        code, out = run(path)
        assert code == 0, "Expected exit 0, got %d" % code
        assert out["valid"] is True
        assert out["errors"] == []
        assert out["stats"]["journeys"] == 1
        assert out["stats"]["steps"] == 2
    print("pass: test_valid_journeys")


def test_missing_journeys_key():
    with tempfile.TemporaryDirectory() as d:
        path = write_json(d, {"version": "1.0"})
        code, out = run(path)
        assert code == 1
        assert out["valid"] is False
        assert any("journeys" in e for e in out["errors"])
    print("pass: test_missing_journeys_key")


def test_duplicate_step_ids():
    with tempfile.TemporaryDirectory() as d:
        path = write_json(d, {
            "journeys": [
                {
                    "id": "j1",
                    "name": "Journey 1",
                    "steps": [
                        {"id": "NAV-01", "action": "go home", "screen": "home", "tested": True},
                    ]
                },
                {
                    "id": "j2",
                    "name": "Journey 2",
                    "steps": [
                        {"id": "NAV-01", "action": "go home again", "screen": "home", "tested": False},
                    ]
                }
            ]
        })
        code, out = run(path)
        assert code == 1
        assert out["valid"] is False
        assert any("duplicate step id" in e for e in out["errors"])
    print("pass: test_duplicate_step_ids")


def test_invalid_step_status():
    with tempfile.TemporaryDirectory() as d:
        path = write_json(d, {
            "journeys": [
                {
                    "id": "j1",
                    "name": "Journey 1",
                    "steps": [
                        {"id": "CHK-01", "action": "check", "screen": "main", "tested": "yes"},
                    ]
                }
            ]
        })
        code, out = run(path)
        assert code == 1
        assert out["valid"] is False
        assert any("tested" in e for e in out["errors"])
    print("pass: test_invalid_step_status")


def test_missing_required_step_fields():
    with tempfile.TemporaryDirectory() as d:
        path = write_json(d, {
            "journeys": [
                {
                    "id": "j1",
                    "name": "Journey 1",
                    "steps": [
                        {"id": "FLD-01"}
                    ]
                }
            ]
        })
        code, out = run(path)
        assert code == 1
        assert out["valid"] is False
        assert any("action" in e for e in out["errors"])
        assert any("screen" in e for e in out["errors"])
        assert any("tested" in e for e in out["errors"])
    print("pass: test_missing_required_step_fields")


def test_partial_without_note():
    with tempfile.TemporaryDirectory() as d:
        path = write_json(d, {
            "journeys": [
                {
                    "id": "j1",
                    "name": "Journey 1",
                    "steps": [
                        {"id": "PAR-01", "action": "partial check", "screen": "main", "tested": "partial"},
                    ]
                }
            ]
        })
        code, out = run(path)
        assert code == 0, "Warnings should not cause failure"
        assert out["valid"] is True
        assert len(out["warnings"]) > 0
        assert any("partial" in w and "note" in w for w in out["warnings"])
    print("pass: test_partial_without_note")


def test_empty_steps_array():
    with tempfile.TemporaryDirectory() as d:
        path = write_json(d, {
            "journeys": [
                {
                    "id": "j1",
                    "name": "Empty Journey",
                    "steps": []
                }
            ]
        })
        code, out = run(path)
        assert code == 1
        assert out["valid"] is False
        assert any("empty" in e for e in out["errors"])
    print("pass: test_empty_steps_array")


if __name__ == "__main__":
    test_valid_journeys()
    test_missing_journeys_key()
    test_duplicate_step_ids()
    test_invalid_step_status()
    test_missing_required_step_fields()
    test_partial_without_note()
    test_empty_steps_array()
    print("\nAll validate-journeys tests passed")
