#!/usr/bin/env python3
"""Tests for the Pathfinder MCP server (mcp/server.py)."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SERVER = os.path.join(REPO, "mcp", "server.py")

_spec = importlib.util.spec_from_file_location("pf_mcp_server", SERVER)
srv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(srv)


def test_initialize_echoes_protocol_and_advertises_tools():
    resp = srv.handle_message({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                               "params": {"protocolVersion": "2025-06-18"}})
    assert resp["result"]["protocolVersion"] == "2025-06-18"
    assert resp["result"]["serverInfo"]["name"] == "pathfinder"
    assert "tools" in resp["result"]["capabilities"]


def test_initialized_notification_has_no_response():
    assert srv.handle_message({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_tools_list_includes_core_tools():
    resp = srv.handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = {t["name"] for t in resp["result"]["tools"]}
    assert {"detect_ui_framework", "coverage_score", "validate_journeys", "generate_diagrams"} <= names
    # every tool advertises an input schema
    assert all("inputSchema" in t for t in resp["result"]["tools"])


def test_initialize_falls_back_to_server_protocol_version():
    resp = srv.handle_message({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["result"]["protocolVersion"] == srv.PROTOCOL_VERSION


def test_unknown_tool_is_invalid_params():
    resp = srv.handle_message({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                               "params": {"name": "nope", "arguments": {}}})
    assert resp["error"]["code"] == -32602  # Invalid params, not Internal error
    assert "unknown tool" in resp["error"]["message"]


def test_unknown_method_is_method_not_found():
    resp = srv.handle_message({"jsonrpc": "2.0", "id": 9, "method": "bogus/method"})
    assert resp["error"]["code"] == -32601


def test_missing_required_arg_is_validation_error():
    resp = srv.handle_message({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                               "params": {"name": "validate_journeys", "arguments": {}}})
    assert resp["error"]["code"] == -32602
    assert "path" in resp["error"]["message"]


def test_arg_builders_insert_double_dash_before_user_paths():
    """A caller must not be able to smuggle CLI flags through a path argument."""
    args = srv.TOOLS["generate_diagrams"]["args"]({"journeys_path": "--save-baseline"})
    assert "--" in args and args.index("--") < args.index("--save-baseline")
    args2 = srv.TOOLS["coverage_score"]["args"]({"journeys_path": "--clear-baseline"})
    assert "--" in args2 and args2.index("--") < args2.index("--clear-baseline")


def test_tools_call_runs_real_script():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "journeys.json")
        with open(p, "w") as f:
            json.dump({"journeys": [{"id": "A", "name": "Flow", "steps": [
                {"id": "A-01", "action": "S1", "screen": "V", "tested": True},
                {"id": "A-02", "action": "S2", "screen": "V", "tested": False}]}]}, f)
        resp = srv.handle_message({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                                   "params": {"name": "coverage_score", "arguments": {"journeys_path": p}}})
        assert resp["result"]["isError"] is False
        payload = json.loads(resp["result"]["content"][0]["text"])
        assert payload["coverage"] == 50.0


def test_stdio_round_trip():
    """The server reads JSON-RPC lines from stdin and writes responses to stdout."""
    msgs = "\n".join([
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
    ]) + "\n"
    proc = subprocess.run([sys.executable, SERVER], input=msgs, capture_output=True, text=True, timeout=30)
    lines = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
    ids = [m.get("id") for m in lines]
    assert 1 in ids and 2 in ids       # two requests answered
    assert all("error" not in m for m in lines)


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
