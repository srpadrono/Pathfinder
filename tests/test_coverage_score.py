#!/usr/bin/env python3
"""Tests for coverage-score.py"""
import json
import os
import subprocess
import tempfile

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "skills", "pathfinder", "scripts", "coverage-score.py")

def test_high_coverage():
    with tempfile.TemporaryDirectory() as d:
        data = {"journeys": [{"id": "A", "name": "Flow", "steps": [
            {"id": "A-01", "action": "S1", "tested": True},
            {"id": "A-02", "action": "S2", "tested": True},
        ]}]}
        p = os.path.join(d, "j.json")
        with open(p, "w") as f:
            json.dump(data, f)
        r = subprocess.run(["python3", SCRIPT, p], capture_output=True, text=True)
        assert r.returncode == 0
        out = json.loads(r.stdout)
        assert out["coverage"] == 100.0
    print("✅ test_high_coverage")

def test_low_coverage_reports_without_failing_by_default():
    """A score command should report, not fail CI, unless a gate is requested."""
    with tempfile.TemporaryDirectory() as d:
        data = {"journeys": [{"id": "A", "name": "Flow", "steps": [
            {"id": "A-01", "action": "S1", "tested": True},
            {"id": "A-02", "action": "S2", "tested": False},
            {"id": "A-03", "action": "S3", "tested": False},
            {"id": "A-04", "action": "S4", "tested": False},
        ]}]}
        p = os.path.join(d, "j.json")
        with open(p, "w") as f:
            json.dump(data, f)
        # Default: reports and exits 0.
        r = subprocess.run(["python3", SCRIPT, p], capture_output=True, text=True)
        assert r.returncode == 0, f"Default run should exit 0, got {r.returncode}: {r.stderr}"
        out = json.loads(r.stdout)
        assert out["coverage"] == 25.0
        # With a gate: exits 1 below the threshold.
        r2 = subprocess.run(["python3", SCRIPT, p, "--fail-under", "50"], capture_output=True, text=True)
        assert r2.returncode == 1, "Should exit 1 when below --fail-under gate"
        assert "below the 50.0% gate" in r2.stderr or "below the 50% gate" in r2.stderr
    print("✅ test_low_coverage_reports_without_failing_by_default")


def test_count_partial_as_tested_via_config():
    with tempfile.TemporaryDirectory() as d:
        pdir = os.path.join(d, "e2e", "tests", "pathfinder")
        os.makedirs(pdir)
        with open(os.path.join(pdir, "config.json"), "w") as f:
            json.dump({"testDir": "e2e/tests", "coverage": {"countPartialAsTested": True}}, f)
        with open(os.path.join(pdir, "journeys.json"), "w") as f:
            json.dump({"journeys": [{"id": "A", "name": "Flow", "steps": [
                {"id": "A-01", "action": "S1", "tested": True},
                {"id": "A-02", "action": "S2", "tested": "partial"},
            ]}]}, f)
        r = subprocess.run(["python3", SCRIPT], cwd=d, capture_output=True, text=True)
        assert r.returncode == 0, f"Failed: {r.stderr}"
        out = json.loads(r.stdout)
        assert out["coverage"] == 100.0, "partial should count when configured"
    print("✅ test_count_partial_as_tested_via_config")

def test_partial_status():
    with tempfile.TemporaryDirectory() as d:
        data = {"journeys": [{"id": "A", "name": "Flow", "steps": [
            {"id": "A-01", "action": "S1", "tested": True},
            {"id": "A-02", "action": "S2", "tested": "partial"},
        ]}]}
        p = os.path.join(d, "j.json")
        with open(p, "w") as f:
            json.dump(data, f)
        r = subprocess.run(["python3", SCRIPT, p], capture_output=True, text=True)
        out = json.loads(r.stdout)
        assert out["partial"] == 1
        # By default, partial does NOT count toward coverage (1 of 2 tested = 50%).
        assert out["coverage"] == 50.0
    print("✅ test_partial_status")


def test_fail_under_gate_via_config():
    with tempfile.TemporaryDirectory() as d:
        pdir = os.path.join(d, "e2e", "tests", "pathfinder")
        os.makedirs(pdir)
        with open(os.path.join(pdir, "config.json"), "w") as f:
            json.dump({"testDir": "e2e/tests", "coverage": {"failUnder": 50}}, f)
        with open(os.path.join(pdir, "journeys.json"), "w") as f:
            json.dump({"journeys": [{"id": "A", "name": "Flow", "steps": [
                {"id": "A-01", "action": "S1", "screen": "V", "tested": True},
                {"id": "A-02", "action": "S2", "screen": "V", "tested": False},
                {"id": "A-03", "action": "S3", "screen": "V", "tested": False},
                {"id": "A-04", "action": "S4", "screen": "V", "tested": False},
            ]}]}, f)
        # 25% < failUnder 50 (from config) → non-zero, no flag needed.
        r = subprocess.run(["python3", SCRIPT], cwd=d, capture_output=True, text=True)
        assert r.returncode == 1, f"config failUnder should gate, got {r.returncode}: {r.stderr}"
        assert "below the 50" in r.stderr
    print("✅ test_fail_under_gate_via_config")


def test_malformed_config_does_not_crash():
    """A non-dict config.json must not crash the score (it falls back to defaults)."""
    with tempfile.TemporaryDirectory() as d:
        pdir = os.path.join(d, "e2e", "tests", "pathfinder")
        os.makedirs(pdir)
        with open(os.path.join(pdir, "config.json"), "w") as f:
            f.write("[1, 2, 3]")  # valid JSON, wrong shape
        with open(os.path.join(pdir, "journeys.json"), "w") as f:
            json.dump({"journeys": [{"id": "A", "name": "Flow", "steps": [
                {"id": "A-01", "action": "S1", "screen": "V", "tested": True}]}]}, f)
        r = subprocess.run(["python3", SCRIPT], cwd=d, capture_output=True, text=True)
        assert r.returncode == 0, f"should not crash on malformed config: {r.stderr}"
        assert json.loads(r.stdout)["coverage"] == 100.0
    print("✅ test_malformed_config_does_not_crash")


def test_auto_detects_canonical_journeys_path():
    with tempfile.TemporaryDirectory() as d:
        pdir = os.path.join(d, "e2e", "tests", "pathfinder")
        os.makedirs(pdir)
        with open(os.path.join(pdir, "config.json"), "w") as f:
            json.dump({"testDir": "e2e/tests"}, f)
        with open(os.path.join(pdir, "journeys.json"), "w") as f:
            json.dump({"journeys": [{"id": "A", "name": "Flow", "steps": [
                {"id": "A-01", "action": "S1", "tested": True},
            ]}]}, f)

        r = subprocess.run(["python3", SCRIPT], cwd=d, capture_output=True, text=True)
        assert r.returncode == 0, f"Failed: {r.stderr}"
        out = json.loads(r.stdout)
        assert out["coverage"] == 100.0
    print("✅ test_auto_detects_canonical_journeys_path")

if __name__ == "__main__":
    test_high_coverage()
    test_low_coverage_reports_without_failing_by_default()
    test_count_partial_as_tested_via_config()
    test_partial_status()
    test_fail_under_gate_via_config()
    test_malformed_config_does_not_crash()
    test_auto_detects_canonical_journeys_path()
    print("\nAll coverage-score tests passed")
