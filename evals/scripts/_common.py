#!/usr/bin/env python3
"""Shared helpers for the Pathfinder eval harness.

The harness is deliberately split into honest layers:

* ``validate_suite.py`` — schema + structural checks (no model, runs in CI).
* ``run_evals.py``       — runs each case A/B (skill available vs. baseline) with a
                           real agent backend, capturing transcript + artifacts.
* ``grade_evals.py``     — an LLM-as-judge grades each expectation (text/passed/
                           evidence, no partial credit). This is the compliant path
                           and needs the ``claude`` CLI logged in (or an API key).
* ``aggregate_benchmark.py`` — variance + with/without delta + non-discriminating
                           assertion analysis.
* ``run_triggering.py``  — does the skill fire when it should and stay quiet on
                           near-misses.

Nothing here fakes a passing grade. Layers that cannot reach a model say so.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent.parent          # evals/
REPO_ROOT = EVALS_DIR.parent                                 # repo root
SKILLS_DIR = REPO_ROOT / "skills"                            # bundled skills
RUNS_DIR = EVALS_DIR / "runs"                                # generated artifacts (gitignored)

SKILL_NAMES = ["pathfinder", "map", "blaze", "scout", "summit"]


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def stage_fixtures(eval_case: dict, project_dir: Path) -> None:
    """Copy an eval's fixture files into the temp project at their target paths."""
    for mapping in eval_case.get("files", []):
        src = EVALS_DIR / mapping["from"]
        dst = project_dir / mapping["to"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


# Files that make up the Pathfinder plugin (what `--plugin-dir` needs to see).
PLUGIN_FILES = [".claude-plugin", "skills", ".mcp.json", "mcp"]


def claude_plugin_flags() -> list[str]:
    """Flags that make Claude Code load the Pathfinder plugin (and its skills) for a
    headless session. Headless `claude -p` does NOT discover a temp project's
    ``.claude/skills/`` — `--plugin-dir` is the mechanism that actually loads the
    skill (it registers as ``pathfinder:<skill>``)."""
    return ["--plugin-dir", str(REPO_ROOT)]


def build_plugin_dir(dest: Path) -> Path:
    """Copy the plugin (manifest + skills + mcp) into ``dest`` so it can be loaded
    via ``--plugin-dir dest`` — used by the optimizer loop, which mutates the copy."""
    dest.mkdir(parents=True, exist_ok=True)
    for name in PLUGIN_FILES:
        src = REPO_ROOT / name
        if src.is_dir():
            shutil.copytree(src, dest / name, symlinks=False, dirs_exist_ok=True)
        elif src.exists():
            shutil.copy2(src, dest / name)
    return dest


def install_skills_for_codex(project_dir: Path) -> None:
    """Make the Pathfinder skills discoverable to Codex (``.agents/skills/``)."""
    dst_root = project_dir / ".agents" / "skills"
    dst_root.mkdir(parents=True, exist_ok=True)
    for name in SKILL_NAMES:
        src = SKILLS_DIR / name
        if src.exists():
            shutil.copytree(src, dst_root / name, symlinks=False, dirs_exist_ok=True)


def snapshot_artifacts(project_dir: Path) -> dict:
    """Return a map of {relative_path: text_content} for files the agent produced.

    Skips the staged skill files, VCS noise, and large/binary blobs so the grader
    sees only what the run actually created or changed.
    """
    artifacts: dict[str, str] = {}
    skip_parts = {".claude", ".agents", ".git", "node_modules", "__pycache__"}
    for path in sorted(project_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(project_dir)
        if skip_parts & set(rel.parts):
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        if len(text) > 20000:
            text = text[:20000] + "\n...[truncated]..."
        artifacts[str(rel)] = text
    return artifacts


def claude_flags() -> list[str]:
    """Flags for headless Claude runs. Override via PATHFINDER_EVAL_CLAUDE_FLAGS."""
    override = os.environ.get("PATHFINDER_EVAL_CLAUDE_FLAGS")
    if override is not None:
        return override.split()
    return ["--permission-mode", "bypassPermissions"]


def have_command(cmd: str) -> bool:
    return shutil.which(cmd) is not None


# Phrases that mean "the model couldn't run" — NOT a skill result. If we see these we
# must abort the eval rather than record a misleading 0% (a limit ≠ the skill failing).
UNAVAILABLE_MARKERS = (
    "session limit", "hit your", "usage limit", "rate limit", "rate_limit",
    "overloaded", "quota", "may not exist or you may not have access",
)


def model_unavailable(text: str) -> bool:
    t = (text or "").lower()
    return any(m in t for m in UNAVAILABLE_MARKERS)


class ModelUnavailable(RuntimeError):
    """Raised when the backend model can't run (session/usage limit, missing model).
    Aborts the eval so an outage is never reported as a skill failure."""


def run_claude_headless(prompt: str, cwd: Path, *, model: str | None = None,
                        timeout: int = 600, extra_flags: list[str] | None = None) -> dict:
    """Run ``claude -p`` non-interactively and return a structured result.

    Pass ``extra_flags`` (e.g. ``claude_plugin_flags()``) to load the skill in the
    with-skill arm. Returns {ok, stdout, stderr, result_text, num_turns, ...}.
    """
    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    if model:
        cmd += ["--model", model]
    cmd += claude_flags()
    if extra_flags:
        cmd += extra_flags
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    out = proc.stdout.strip()
    parsed: dict = {}
    try:
        parsed = json.loads(out)
    except json.JSONDecodeError:
        parsed = {}
    result_text = parsed.get("result", out)
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": out,
        "stderr": proc.stderr[-4000:],
        "result_text": result_text,
        "is_error": bool(parsed.get("is_error")) or model_unavailable(result_text),
        "unavailable": model_unavailable(result_text) or model_unavailable(proc.stderr),
        "num_turns": parsed.get("num_turns"),
        "total_cost_usd": parsed.get("total_cost_usd"),
        "duration_ms": parsed.get("duration_ms"),
    }


def run_codex_headless(prompt: str, cwd: Path, *, timeout: int = 600) -> dict:
    """Run ``codex exec --json`` non-interactively and return a structured result."""
    cmd = ["codex", "exec", "--json", "--full-auto", prompt]
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    events = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": proc.stdout[-20000:],
        "stderr": proc.stderr[-4000:],
        "result_text": proc.stdout[-20000:],
        "events": events,
    }
