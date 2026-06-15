#!/usr/bin/env python3
"""Tests for the central config loader (skills/pathfinder/scripts/pathfinder_config.py)."""
import json
import os
import sys
import tempfile

SCRIPTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills", "pathfinder", "scripts"))
sys.path.insert(0, SCRIPTS)

import pathfinder_config as cfg  # noqa: E402


def test_defaults_when_no_config():
    with tempfile.TemporaryDirectory() as d:
        c = cfg.load_config(d)
        assert c["coverage"]["thresholds"] == {"excellent": 80, "acceptable": 50}
        assert c["coverage"]["countPartialAsTested"] is False
        assert c["coverage"]["failUnder"] is None
        assert c["ignore"] == []


def test_user_config_deep_merges_over_defaults():
    with tempfile.TemporaryDirectory() as d:
        pdir = os.path.join(d, "e2e", "pathfinder")
        os.makedirs(pdir)
        with open(os.path.join(pdir, "config.json"), "w") as f:
            json.dump({"coverage": {"thresholds": {"excellent": 95}}, "ignore": ["**/admin/**"]}, f)
        c = cfg.load_config(d)
        # overridden value...
        assert c["coverage"]["thresholds"]["excellent"] == 95
        # ...while the unspecified sibling keeps its default (deep merge, not replace)
        assert c["coverage"]["thresholds"]["acceptable"] == 50
        assert c["ignore"] == ["**/admin/**"]


def test_status_bar_honors_thresholds():
    config = {"coverage": {"thresholds": {"excellent": 90, "acceptable": 60}}}
    assert cfg.status_bar(95, config) == "🟢"
    assert cfg.status_bar(70, config) == "🟡"
    assert cfg.status_bar(40, config) == "🔴"
    # boundary is inclusive
    assert cfg.status_bar(90, config) == "🟢"
    assert cfg.status_bar(60, config) == "🟡"


def test_coverage_thresholds_returns_floats():
    e, a = cfg.coverage_thresholds(cfg.DEFAULTS)
    assert (e, a) == (80.0, 50.0)


def test_malformed_config_falls_back_to_defaults():
    """A non-dict config.json (or mis-typed sections) must never crash a consumer."""
    with tempfile.TemporaryDirectory() as d:
        pdir = os.path.join(d, "e2e", "pathfinder")
        os.makedirs(pdir)
        with open(os.path.join(pdir, "config.json"), "w") as f:
            f.write('[1,2,3]')  # valid JSON, wrong top-level shape
        c = cfg.load_config(d)
        assert c["coverage"]["thresholds"] == {"excellent": 80, "acceptable": 50}
        assert c["ignore"] == []


def test_mistyped_sections_are_coerced():
    with tempfile.TemporaryDirectory() as d:
        pdir = os.path.join(d, "e2e", "pathfinder")
        os.makedirs(pdir)
        with open(os.path.join(pdir, "config.json"), "w") as f:
            json.dump({"coverage": None, "ignore": "**/admin/**"}, f)  # both wrong types
        c = cfg.load_config(d)
        assert isinstance(c["coverage"], dict)
        assert c["coverage"]["thresholds"]["excellent"] == 80
        assert c["ignore"] == []  # string coerced back to the list default
        # the defensive helper also survives a mis-typed coverage value
        assert cfg.coverage_thresholds({"coverage": None}) == (80.0, 50.0)


def test_status_bar_survives_mistyped_config():
    assert cfg.status_bar(95, {"coverage": "nonsense"}) == "🟢"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
