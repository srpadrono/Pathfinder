#!/usr/bin/env python3
"""Tests for coverage-score.py"""
import subprocess, json, tempfile, os

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "skill", "scripts", "coverage-score.py")

def test_high_coverage():
    with tempfile.TemporaryDirectory() as d:
        data = {"journeys": [{"id": "A", "name": "Flow", "steps": [
            {"id": "A-01", "action": "S1", "tested": True},
            {"id": "A-02", "action": "S2", "tested": True},
        ]}]}
        p = os.path.join(d, "j.json")
        with open(p, "w") as f: json.dump(data, f)
        r = subprocess.run(["python3", SCRIPT, p], capture_output=True, text=True)
        assert r.returncode == 0
        out = json.loads(r.stdout)
        assert out["coverage"] == 100.0
    print("✅ test_high_coverage")

def test_low_coverage_exits_1():
    with tempfile.TemporaryDirectory() as d:
        data = {"journeys": [{"id": "A", "name": "Flow", "steps": [
            {"id": "A-01", "action": "S1", "tested": True},
            {"id": "A-02", "action": "S2", "tested": False},
            {"id": "A-03", "action": "S3", "tested": False},
            {"id": "A-04", "action": "S4", "tested": False},
        ]}]}
        p = os.path.join(d, "j.json")
        with open(p, "w") as f: json.dump(data, f)
        r = subprocess.run(["python3", SCRIPT, p], capture_output=True, text=True)
        assert r.returncode == 1, "Should exit 1 for <50% coverage"
        out = json.loads(r.stdout)
        assert out["coverage"] == 25.0
    print("✅ test_low_coverage_exits_1")

def test_partial_status():
    with tempfile.TemporaryDirectory() as d:
        data = {"journeys": [{"id": "A", "name": "Flow", "steps": [
            {"id": "A-01", "action": "S1", "tested": "partial"},
        ]}]}
        p = os.path.join(d, "j.json")
        with open(p, "w") as f: json.dump(data, f)
        r = subprocess.run(["python3", SCRIPT, p], capture_output=True, text=True)
        out = json.loads(r.stdout)
        assert out["partial"] == 1
    print("✅ test_partial_status")

if __name__ == "__main__":
    test_high_coverage()
    test_low_coverage_exits_1()
    test_partial_status()
    print("\nAll coverage-score tests passed")
