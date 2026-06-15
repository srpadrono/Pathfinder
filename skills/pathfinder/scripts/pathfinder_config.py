#!/usr/bin/env python3
"""Load and merge Pathfinder project config (config.json) with defaults.

Every configurable behaviour reads through here so the defaults live in one place
and match skills/pathfinder/schema/config.schema.json. Missing config is fine —
callers get the documented defaults.
"""
from __future__ import annotations

import copy

from pathfinder_paths import _load_json, find_pathfinder_config

DEFAULTS: dict = {
    "coverage": {
        "thresholds": {"excellent": 80, "acceptable": 50},
        "countPartialAsTested": False,
        "failUnder": None,
    },
    "ignore": [],
    "commands": {},
    "selectors": {"strategy": "accessibility-first", "testIdAttribute": None},
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, val in (override or {}).items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def load_config(root: str = ".") -> dict:
    """Return the project config merged over defaults (always a full, well-typed dict).

    A malformed config.json never crashes a consumer: a non-dict top-level value is
    ignored entirely, and any section whose type doesn't match the default's type is
    dropped back to its default (so e.g. `"ignore": "x"` or `"coverage": null` is safe)."""
    config_path = find_pathfinder_config(root)
    user = _load_json(config_path) if config_path else None  # _load_json returns dict|None
    merged = _deep_merge(DEFAULTS, user or {})
    # Coerce mis-typed sections back to their default shape.
    for key, default in DEFAULTS.items():
        if not isinstance(merged.get(key), type(default)):
            merged[key] = copy.deepcopy(default)
    if not isinstance(merged.get("coverage", {}).get("thresholds"), dict):
        merged["coverage"]["thresholds"] = copy.deepcopy(DEFAULTS["coverage"]["thresholds"])
    return merged


def coverage_thresholds(config: dict) -> tuple[float, float]:
    """Return (excellent, acceptable) percent cutoffs. Defensive against mis-typed config."""
    cov = config.get("coverage")
    cov = cov if isinstance(cov, dict) else {}
    t = cov.get("thresholds")
    t = t if isinstance(t, dict) else {}
    default = DEFAULTS["coverage"]["thresholds"]
    try:
        excellent = float(t.get("excellent", default["excellent"]))
        acceptable = float(t.get("acceptable", default["acceptable"]))
    except (TypeError, ValueError):
        excellent, acceptable = float(default["excellent"]), float(default["acceptable"])
    return excellent, acceptable


def status_bar(coverage: float, config: dict) -> str:
    """🟢/🟡/🔴 marker for a coverage percent, honoring configured thresholds."""
    excellent, acceptable = coverage_thresholds(config)
    if coverage >= excellent:
        return "🟢"
    if coverage >= acceptable:
        return "🟡"
    return "🔴"
