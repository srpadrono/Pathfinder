# Pathfinder MCP server

A dependency-free [MCP](https://modelcontextprotocol.io) server that exposes
Pathfinder's deterministic tools to any MCP client (Claude Code, Codex, Cursor, …).
It's a thin wrapper around the same scripts the skill uses — one implementation,
one set of tests — speaking JSON-RPC 2.0 over stdio with only the Python stdlib.

## Tools

| Tool | Does |
|------|------|
| `detect_ui_framework` | Detect the UI test framework + platform |
| `scan_test_coverage` | Map tests to routes/screens, report route coverage |
| `coverage_score` | Compute the coverage score from a `journeys.json` |
| `validate_journeys` | Validate a `journeys.json` against the schema |
| `generate_diagrams` | Generate Mermaid coverage diagrams (writes `blazes.md`) |

## Use it

Installed automatically with the Claude Code plugin (registered via
[`.mcp.json`](../.mcp.json) → `${CLAUDE_PLUGIN_ROOT}/mcp/server.py`).

For any other MCP client, point it at the server command:

```json
{
  "mcpServers": {
    "pathfinder": { "command": "python3", "args": ["/abs/path/to/Pathfinder/mcp/server.py"] }
  }
}
```

Smoke test it by hand:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 mcp/server.py
```

> The MCP server complements the skill (it does not replace it). The skill drives the
> full map → blaze → scout → summit workflow; the MCP tools are handy when you want a
> single deterministic operation from a non-Claude-Code client.
