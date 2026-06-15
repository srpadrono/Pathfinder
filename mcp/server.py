#!/usr/bin/env python3
"""Pathfinder MCP server — exposes the deterministic Pathfinder tools to any MCP
client (Claude Code, Codex, Cursor, …) over stdio.

This is a thin, dependency-free wrapper around the same scripts the skill uses, so
there is one implementation and one set of tests. It speaks JSON-RPC 2.0 over
stdio (the MCP transport) using only the Python standard library.

Tools:
  detect_ui_framework   Detect the UI test framework in a project.
  scan_test_coverage    Map test files to routes/screens and report route coverage.
  coverage_score        Compute the coverage score from a journeys.json.
  validate_journeys     Validate a journeys.json against the schema.
  generate_diagrams     Generate Mermaid coverage diagrams (writes blazes.md).

Run directly for a quick check:  echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 mcp/server.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "pathfinder" / "scripts"
PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "pathfinder", "version": "3.0.0"}

# tool name -> (script filename, builds the argv tail from arguments)
TOOLS: dict[str, dict] = {
    "detect_ui_framework": {
        "script": "detect-ui-framework.py",
        "description": "Detect the UI test framework (Playwright, Cypress, XCUITest, …) and platform for a project.",
        "schema": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Project root (default '.')."}}},
        "args": lambda a: [a.get("path", ".")],
    },
    "scan_test_coverage": {
        "script": "scan-test-coverage.py",
        "description": "Scan a project for UI test files, map them to routes/screens, and report route coverage.",
        "schema": {"type": "object", "properties": {"path": {"type": "string"}}},
        "args": lambda a: [a.get("path", ".")],
    },
    "coverage_score": {
        "script": "coverage-score.py",
        "description": "Compute the test coverage score from a journeys.json (auto-detected if omitted).",
        "schema": {"type": "object", "properties": {
            "journeys_path": {"type": "string"},
            "fail_under": {"type": "number", "description": "Exit non-zero below this percent."}}},
        # `--` stops flag parsing so a caller can't smuggle CLI flags via journeys_path.
        "args": lambda a: (["--fail-under", str(a["fail_under"])] if a.get("fail_under") is not None else [])
                          + (["--", a["journeys_path"]] if a.get("journeys_path") else []),
    },
    "validate_journeys": {
        "script": "validate-journeys.py",
        "description": "Validate a journeys.json file's structure against the Pathfinder schema.",
        "schema": {"type": "object", "required": ["path"], "properties": {"path": {"type": "string"}}},
        "args": lambda a: ["--", a["path"]],
    },
    "generate_diagrams": {
        "script": "generate-diagrams.py",
        "description": "Generate Mermaid coverage diagrams from a journeys.json (writes blazes.md next to it).",
        "schema": {"type": "object", "properties": {
            "journeys_path": {"type": "string"}, "output": {"type": "string"}}},
        "args": lambda a: (["--output", a["output"]] if a.get("output") else [])
                          + (["--", a["journeys_path"]] if a.get("journeys_path") else []),
    },
}


class RpcError(Exception):
    """A JSON-RPC error carrying a spec error code."""
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


def _run_tool(name: str, arguments: dict) -> dict:
    spec = TOOLS[name]
    cmd = ["python3", str(SCRIPTS / spec["script"]), *spec["args"](arguments or {})]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    text = proc.stdout or ""
    if proc.returncode != 0 and proc.stderr:
        text = (text + "\n" + proc.stderr).strip()
    return {
        "content": [{"type": "text", "text": text or "(no output)"}],
        "isError": proc.returncode != 0,
    }


def dispatch(method: str, params: dict, msg_id):
    """Pure request router. Returns a JSON-RPC result dict, or None for notifications."""
    if method == "initialize":
        version = (params or {}).get("protocolVersion", PROTOCOL_VERSION)
        return {"protocolVersion": version,
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO}
    if method in ("notifications/initialized", "initialized"):
        return None  # notification, no response
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": [
            {"name": n, "description": t["description"], "inputSchema": t["schema"]}
            for n, t in TOOLS.items()
        ]}
    if method == "tools/call":
        name = (params or {}).get("name")
        if name not in TOOLS:
            raise RpcError(-32602, f"unknown tool: {name}")  # Invalid params
        arguments = (params or {}).get("arguments") or {}
        required = TOOLS[name]["schema"].get("required", [])
        missing = [r for r in required if r not in arguments]
        if missing:
            raise RpcError(-32602, f"missing required argument(s): {', '.join(missing)}")
        return _run_tool(name, arguments)
    raise RpcError(-32601, f"unknown method: {method}")  # Method not found


def handle_message(msg: dict) -> dict | None:
    """Wrap dispatch with JSON-RPC envelope + error handling."""
    msg_id = msg.get("id")
    method = msg.get("method", "")
    try:
        result = dispatch(method, msg.get("params") or {}, msg_id)
    except RpcError as exc:
        if msg_id is None:
            return None
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": exc.code, "message": str(exc)}}
    except Exception as exc:  # noqa: BLE001 — surface as a JSON-RPC error, never crash
        if msg_id is None:
            return None
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32603, "message": str(exc)}}
    if result is None or msg_id is None:
        return None
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def serve() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = handle_message(msg)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    serve()
