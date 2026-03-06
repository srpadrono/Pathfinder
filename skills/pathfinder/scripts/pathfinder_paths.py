#!/usr/bin/env python3
"""Helpers for locating Pathfinder artifacts in a project tree."""
import json
import os


SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def _candidate_rank(path):
    normalized = os.path.normpath(path).replace("\\", "/")
    depth = normalized.count("/")
    is_legacy = "/.pathfinder/" in normalized
    return (1 if is_legacy else 0, depth, normalized)


def _walk_pathfinder_files(root, filename):
    root = os.path.abspath(root)
    candidates = []

    legacy = os.path.join(root, ".pathfinder", filename)
    if os.path.exists(legacy):
        candidates.append(os.path.normpath(legacy))

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS and not name.startswith(".")]
        if os.path.basename(dirpath) == "pathfinder" and filename in filenames:
            candidates.append(os.path.normpath(os.path.join(dirpath, filename)))

    return sorted(set(candidates), key=_candidate_rank)


def _load_json(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def find_pathfinder_config(root="."):
    candidates = _walk_pathfinder_files(root, "config.json")
    return candidates[0] if candidates else None


def find_journeys_file(root="."):
    root = os.path.abspath(root)
    config_path = find_pathfinder_config(root)

    if config_path:
        config = _load_json(config_path) or {}
        test_dir = config.get("testDir")
        if isinstance(test_dir, str) and test_dir:
            configured = os.path.normpath(os.path.join(root, test_dir, "pathfinder", "journeys.json"))
            if os.path.exists(configured):
                return configured

        sibling = os.path.normpath(os.path.join(os.path.dirname(config_path), "journeys.json"))
        if os.path.exists(sibling):
            return sibling

    candidates = _walk_pathfinder_files(root, "journeys.json")
    return candidates[0] if candidates else None


def find_pathfinder_dir(root="."):
    root = os.path.abspath(root)
    config_path = find_pathfinder_config(root)

    if config_path:
        config = _load_json(config_path) or {}
        test_dir = config.get("testDir")
        if isinstance(test_dir, str) and test_dir:
            return os.path.normpath(os.path.join(root, test_dir, "pathfinder"))
        return os.path.normpath(os.path.dirname(config_path))

    journeys_path = find_journeys_file(root)
    if journeys_path:
        return os.path.normpath(os.path.dirname(journeys_path))

    legacy = os.path.join(root, ".pathfinder")
    if os.path.isdir(legacy):
        return os.path.normpath(legacy)

    return os.path.normpath(os.path.join(root, "pathfinder"))
