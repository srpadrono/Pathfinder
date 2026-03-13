#!/usr/bin/env python3
"""Generate Mermaid flowchart diagrams from journeys.json.

Usage: python3 generate-diagrams.py [<testDir>/pathfinder/journeys.json] [--output <testDir>/pathfinder/blazes.md]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict

from pathfinder_paths import find_journeys_file

JOURNEY_ICONS = {
    "auth": "🔐", "authentication": "🔐", "login": "🔐",
    "dashboard": "📊", "home": "🏠",
    "report": "📄", "reports": "📄",
    "upload": "📤", "file": "📁",
    "chat": "💬", "message": "💬",
    "settings": "⚙️", "profile": "👤",
    "well": "🛢️", "wells": "🛢️",
    "notification": "🔔", "alert": "🔔",
    "search": "🔍", "onboarding": "🚀",
    "payment": "💳", "billing": "💳",
}


def validate_journey_structure(journeys: list[dict]) -> None:
    """Validate that every journey has required fields. Exit 1 on failure."""
    errors: list[str] = []
    for i, journey in enumerate(journeys):
        prefix = f"journey[{i}]"
        for field in ("id", "name", "steps"):
            if field not in journey:
                errors.append(f"{prefix}: missing required field \"{field}\"")
        steps = journey.get("steps")
        if steps is not None and not isinstance(steps, list):
            errors.append(f"{prefix}: \"steps\" must be a list")
        elif isinstance(steps, list):
            for si, step in enumerate(steps):
                sp = f"{prefix}.steps[{si}]"
                for field in ("id", "action", "screen"):
                    if field not in step:
                        errors.append(f"{sp}: missing required field \"{field}\"")
                if "tested" not in step:
                    errors.append(f"{sp}: missing required field \"tested\"")
                else:
                    tested = step["tested"]
                    if tested is not True and tested is not False and tested != "partial":
                        errors.append(
                            f"{sp}: \"tested\" must be true, false,"
                            f" or \"partial\" (got {json.dumps(tested)})"
                        )
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)


def get_icon(journey_name: str) -> str:
    name_lower = journey_name.lower()
    for key, icon in JOURNEY_ICONS.items():
        if key in name_lower:
            return icon
    return "📋"


def sanitize_id(text: str) -> str:
    """Create a safe Mermaid node id."""
    return re.sub(r"[^a-zA-Z0-9]", "_", text).strip("_")


def sanitize_label(text: str) -> str:
    """Escape characters that break Mermaid label parsing."""
    return text.replace("(", "[").replace(")", "]").replace('"', "'")


def step_status(step: dict) -> tuple[bool, bool, str]:
    """Return (is_tested, is_partial, marker) for a step."""
    is_tested = step.get("tested") is True
    is_partial = step.get("tested") == "partial"
    marker = "✅" if is_tested else "⚠️" if is_partial else "❌"
    return is_tested, is_partial, marker


def style_line(node_id: str, step: dict) -> str:
    """Return the Mermaid style line for a node."""
    if step.get("tested") is True:
        return f"    style {node_id} fill:#2ea043,stroke:#1a7f37,color:#fff"
    elif step.get("tested") == "partial":
        return f"    style {node_id} fill:#d29922,stroke:#b87d14,color:#fff"
    else:
        return f"    style {node_id} fill:#f85149,stroke:#da3633,color:#fff"


def node_declaration(node_id: str, label: str, is_tested: bool, is_partial: bool) -> str:
    """Return the Mermaid node declaration."""
    quoted = f'"{label}"'
    if is_tested:
        return f"    {node_id}({quoted})"
    elif is_partial:
        return f"    {node_id}[/{quoted}/]"
    else:
        return f"    {node_id}[{quoted}]"


def _build_node_graph(journeys: list[dict]) -> tuple[
    dict[str, dict],
    list[str],
    defaultdict[str, set],
    defaultdict[str, list],
    dict[tuple[str, str], dict],
]:
    """Build the node graph from journeys: nodes, roots, incoming, outgoing, edge_meta."""
    nodes: dict[str, dict] = {}
    roots: list[str] = []
    incoming: defaultdict[str, set] = defaultdict(set)
    outgoing: defaultdict[str, list] = defaultdict(list)
    edge_meta: dict[tuple[str, str], dict] = {}
    error_anchor_candidates: defaultdict[str, list] = defaultdict(list)

    for journey in journeys:
        steps = journey.get("steps", [])
        is_error_journey = journey.get("id", "").upper() == "ERROR"
        for step in steps:
            node_id = sanitize_id(step["id"])
            if node_id not in nodes:
                nodes[node_id] = step
            if not is_error_journey:
                action = step.get("action", "").lower()
                if "loading" in action or "api" in action:
                    screen = step.get("screen", "Main")
                    if node_id not in error_anchor_candidates[screen]:
                        error_anchor_candidates[screen].append(node_id)

    for journey in journeys:
        steps = journey.get("steps", [])
        prev_id = None
        prev_screen = None
        is_error_journey = journey.get("id", "").upper() == "ERROR"
        for index, step in enumerate(steps):
            node_id = sanitize_id(step["id"])
            if index == 0:
                attached_to_error_anchor = False
                if is_error_journey:
                    screen = step.get("screen", "Main")
                    anchors = error_anchor_candidates.get(screen, [])
                    if anchors:
                        anchor_id = anchors[-1]
                        if node_id not in outgoing[anchor_id]:
                            outgoing[anchor_id].append(node_id)
                        incoming[node_id].add(anchor_id)
                        edge_meta.setdefault(
                            (anchor_id, node_id),
                            {
                                "label": "⚡ API Error",
                                "cross_screen": True,
                                "kind": "error",
                            },
                        )
                        attached_to_error_anchor = True
                if not attached_to_error_anchor and node_id not in roots:
                    roots.append(node_id)
            if prev_id:
                if node_id not in outgoing[prev_id]:
                    outgoing[prev_id].append(node_id)
                incoming[node_id].add(prev_id)
                edge_meta.setdefault(
                    (prev_id, node_id),
                    {
                        "label": step.get("action", step["id"]),
                        "cross_screen": prev_screen != step.get("screen", "Main"),
                        "kind": "normal",
                    },
                )

            prev_id = node_id
            prev_screen = step.get("screen", "Main")

    return nodes, roots, incoming, outgoing, edge_meta


def _render_walk(
    nodes: dict[str, dict],
    roots: list[str],
    incoming: defaultdict[str, set],
    outgoing: defaultdict[str, list],
    edge_meta: dict[tuple[str, str], dict],
) -> tuple[list[str], list[str]]:
    """Walk the graph and render Mermaid lines and styles."""
    lines: list[str] = []
    styles: list[str] = []
    declared_nodes: set[str] = set()
    declared_decisions: set[str] = set()
    declared_edges: set[str] = set()

    def declare_step(node_id: str) -> None:
        if node_id in declared_nodes:
            return
        step = nodes[node_id]
        is_tested, is_partial, marker = step_status(step)
        label = sanitize_label(f"{marker} {step.get('action', node_id)}")
        lines.append(node_declaration(node_id, label, is_tested, is_partial))
        styles.append(style_line(node_id, step))
        declared_nodes.add(node_id)

    def declare_decision(source_id: str) -> str:
        decision_id = f"{source_id}_decision"
        if decision_id not in declared_decisions:
            declared_decisions.add(decision_id)
            lines.append(f'    {decision_id}{{{{"🔀 User action?"}}}}')
            styles.append(f"    style {decision_id} fill:#1f6feb,stroke:#1158c7,color:#fff")
        edge = f"    {source_id} --> {decision_id}"
        if edge not in declared_edges:
            lines.append(edge)
            declared_edges.add(edge)
        return decision_id

    walked: set[str] = set()

    def walk(node_id: str) -> None:
        if node_id in walked:
            return
        walked.add(node_id)
        declare_step(node_id)

        children = outgoing.get(node_id, [])
        error_children = [child_id for child_id in children if edge_meta[(node_id, child_id)].get("kind") == "error"]
        normal_children = [child_id for child_id in children if edge_meta[(node_id, child_id)].get("kind") != "error"]

        for child_id in error_children:
            declare_step(child_id)
            edge = f'    {node_id} -.->|"⚡ API Error"| {child_id}'
            if edge not in declared_edges:
                lines.append(edge)
                declared_edges.add(edge)
            walk(child_id)

        if len(normal_children) > 1:
            decision_id = declare_decision(node_id)
            for child_id in normal_children:
                declare_step(child_id)
                label = sanitize_label(edge_meta[(node_id, child_id)]["label"])
                edge = f'    {decision_id} -->|"{label}"| {child_id}'
                if edge not in declared_edges:
                    lines.append(edge)
                    declared_edges.add(edge)
                walk(child_id)
            return

        if len(normal_children) == 1:
            child_id = normal_children[0]
            declare_step(child_id)
            arrow = " -.-> " if edge_meta[(node_id, child_id)]["cross_screen"] else " --> "
            edge = f"    {node_id}{arrow}{child_id}"
            if edge not in declared_edges:
                lines.append(edge)
                declared_edges.add(edge)
            walk(child_id)

    ordered_roots = roots + [node_id for node_id in nodes if not incoming.get(node_id) and node_id not in roots]
    for root_id in ordered_roots:
        walk(root_id)
    for node_id in nodes:
        walk(node_id)

    return lines, styles


def build_decision_tree(journeys: list[dict]) -> list[str]:
    """Build a single Mermaid flowchart showing all journeys as a graph."""
    nodes, roots, incoming, outgoing, edge_meta = _build_node_graph(journeys)
    body_lines, styles = _render_walk(nodes, roots, incoming, outgoing, edge_meta)

    lines: list[str] = ["flowchart TD"]
    lines.extend(body_lines)
    lines.extend(styles)
    return lines


def build_flowchart(journey: dict) -> list[str]:
    """Build a Mermaid flowchart for one journey (basic, no cross-journey context)."""
    steps = journey.get("steps", [])
    if not steps:
        return []

    lines: list[str] = []
    lines.append("flowchart TD")

    # Group steps by screen for subgraphs
    screens: dict[str, list[tuple[str, str, bool, bool]]] = {}
    node_ids: list[str] = []

    for i, step in enumerate(steps):
        screen = step.get("screen", "Main")
        action = step.get("action", step.get("id", f"step_{i}"))
        step_id = step.get("id", f"step_{i}")
        node_id = sanitize_id(f"{step_id}_{i}")
        node_ids.append(node_id)

        is_tested = step.get("tested") is True
        is_partial = step.get("tested") == "partial"
        marker = "✅" if is_tested else "⚠️" if is_partial else "❌"
        label = sanitize_label(f"{marker} {action}")

        if screen not in screens:
            screens[screen] = []
        screens[screen].append((node_id, label, is_tested, is_partial))

    # Render subgraphs (one per screen)
    for screen, screen_nodes in screens.items():
        if len(screens) > 1:
            lines.append(f"    subgraph {screen}")
        for node_id, label, is_tested, is_partial in screen_nodes:
            quoted = f'"{label}"'
            if is_tested:
                lines.append(f"        {node_id}({quoted})")
            elif is_partial:
                lines.append(f"        {node_id}[/{quoted}/]")
            else:
                lines.append(f"        {node_id}[{quoted}]")
        if len(screens) > 1:
            lines.append("    end")

    # Edges: connect steps in order
    for i in range(len(node_ids) - 1):
        # Dotted arrow between screens, solid within
        screen_a = steps[i].get("screen", "Main")
        screen_b = steps[i + 1].get("screen", "Main")
        if screen_a != screen_b:
            lines.append(f"    {node_ids[i]} -.-> {node_ids[i+1]}")
        else:
            lines.append(f"    {node_ids[i]} --> {node_ids[i+1]}")

    # Style nodes by coverage status
    for i, step in enumerate(steps):
        node_id = node_ids[i]
        if step.get("tested") is True:
            lines.append(f"    style {node_id} fill:#2ea043,stroke:#1a7f37,color:#fff")
        elif step.get("tested") == "partial":
            lines.append(f"    style {node_id} fill:#d29922,stroke:#b87d14,color:#fff")
        else:
            lines.append(f"    style {node_id} fill:#f85149,stroke:#da3633,color:#fff")

    return lines


def _build_branch_map(all_journeys: list[dict]) -> dict[str, list[tuple[str, str]]]:
    """Build a map of step_id -> list of (next_step_id, next_action) across all journeys.

    This detects where a shared step leads to different next steps in different journeys,
    i.e. decision/branching points.
    """
    branch_map: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for journey in all_journeys:
        steps = journey.get("steps", [])
        for i in range(len(steps) - 1):
            sid = steps[i].get("id", "")
            next_sid = steps[i + 1].get("id", "")
            next_action = steps[i + 1].get("action", next_sid)
            pair = (next_sid, next_action)
            if pair not in branch_map[sid]:
                branch_map[sid].append(pair)
    return branch_map


def _build_error_screen_map(all_journeys: list[dict]) -> dict[str, list[dict]]:
    """Map screen names to error steps that occur on those screens."""
    error_map: defaultdict[str, list[dict]] = defaultdict(list)
    for journey in all_journeys:
        if journey.get("id", "").upper() != "ERROR":
            continue
        for step in journey.get("steps", []):
            screen = step.get("screen", "")
            if screen:
                error_map[screen].append(step)
    return dict(error_map)


def build_journey_flowchart(journey: dict, all_journeys: list[dict]) -> list[str]:
    """Build a Mermaid flowchart for one journey with decision diamonds from cross-journey context.

    When a step in this journey is a branching point (leads to different next steps in
    other journeys), a decision diamond is shown with the current journey's path highlighted
    and other branches shown as greyed-out alternatives.
    """
    steps = journey.get("steps", [])
    if not steps:
        return []

    branch_map = _build_branch_map(all_journeys)
    error_screen_map = _build_error_screen_map(all_journeys)

    lines: list[str] = []
    lines.append("flowchart TD")
    styles: list[str] = []

    # Build node info for this journey's steps
    journey_step_ids: list[str] = []
    step_lookup: dict[str, dict] = {}
    for step in steps:
        sid = step.get("id", "")
        journey_step_ids.append(sid)
        step_lookup[sid] = step

    # Track which node IDs we've declared
    declared: set[str] = set()

    def declare_node(sid: str, step: dict) -> str:
        node_id = sanitize_id(sid)
        if node_id in declared:
            return node_id
        declared.add(node_id)
        is_tested = step.get("tested") is True
        is_partial = step.get("tested") == "partial"
        marker = "✅" if is_tested else "⚠️" if is_partial else "❌"
        label = sanitize_label(f"{marker} {step.get('action', sid)}")
        lines.append(node_declaration(node_id, label, is_tested, is_partial))
        styles.append(style_line(node_id, step))
        return node_id

    # Group steps by screen for subgraph rendering
    screen_order: list[str] = []
    screen_steps: dict[str, list[str]] = defaultdict(list)
    for step in steps:
        screen = step.get("screen", "Main")
        sid = step.get("id", "")
        if screen not in screen_order:
            screen_order.append(screen)
        if sid not in screen_steps[screen]:
            screen_steps[screen].append(sid)

    # Render subgraphs
    multi_screen = len(screen_order) > 1
    for screen in screen_order:
        if multi_screen:
            lines.append(f"    subgraph {screen}")
        for sid in screen_steps[screen]:
            step = step_lookup.get(sid, {})
            declare_node(sid, step)
        if multi_screen:
            lines.append("    end")

    # Render edges with decision diamonds at branching points
    for i in range(len(journey_step_ids) - 1):
        sid = journey_step_ids[i]
        next_sid = journey_step_ids[i + 1]
        node_id = sanitize_id(sid)
        next_node_id = sanitize_id(next_sid)

        branches = branch_map.get(sid, [])
        cross_screen = step_lookup.get(sid, {}).get("screen", "") != step_lookup.get(next_sid, {}).get("screen", "")

        if len(branches) > 1:
            # This is a decision point — show diamond
            decision_id = f"{node_id}_decision"
            if decision_id not in declared:
                declared.add(decision_id)
                lines.append(f'    {decision_id}{{"🔀 Choose path"}}')
                styles.append(f"    style {decision_id} fill:#1f6feb,stroke:#1158c7,color:#fff")
                lines.append(f"    {node_id} --> {decision_id}")

            # Current journey's path (bold arrow)
            next_action = sanitize_label(step_lookup.get(next_sid, {}).get("action", next_sid))
            arrow = " -.-> " if cross_screen else " --> "
            lines.append(f'    {decision_id}{arrow}|"{next_action}"| {next_node_id}')

            # Other branches (greyed out alternatives)
            for alt_sid, alt_action in branches:
                if alt_sid == next_sid:
                    continue
                alt_node_id = sanitize_id(alt_sid)
                if alt_node_id not in declared:
                    declared.add(alt_node_id)
                    alt_label = sanitize_label(f"↗ {alt_action}")
                    lines.append(f'    {alt_node_id}["{alt_label}"]')
                    styles.append(f"    style {alt_node_id} fill:#484f58,stroke:#6e7681,color:#8b949e")
                lines.append(f'    {decision_id} -.->|"{sanitize_label(alt_action)}"| {alt_node_id}')
        else:
            # Simple edge, no branching
            arrow = " -.-> " if cross_screen else " --> "
            lines.append(f"    {node_id}{arrow}{next_node_id}")

        # Check for error branches from this step's screen
        screen = step_lookup.get(sid, {}).get("screen", "")
        action_lower = step_lookup.get(sid, {}).get("action", "").lower()
        if ("api" in action_lower or "loading" in action_lower or "oauth" in action_lower
                or "authenticat" in action_lower or "import" in action_lower or "download" in action_lower):
            error_steps = error_screen_map.get(screen, [])
            for err_step in error_steps:
                err_sid = err_step.get("id", "")
                err_node_id = sanitize_id(err_sid)
                if err_node_id not in declared:
                    declared.add(err_node_id)
                    tested = err_step.get("tested")
                    err_marker = "✅" if tested is True else "⚠️" if tested == "partial" else "❌"
                    err_label = sanitize_label(f"{err_marker} {err_step.get('action', err_sid)}")
                    lines.append(f'    {err_node_id}["{err_label}"]')
                    styles.append(style_line(err_node_id, err_step))
                lines.append(f'    {node_id} -.->|"⚡ Error"| {err_node_id}')

    lines.extend(styles)
    return lines


def compute_coverage(journeys: list[dict]) -> tuple[int, int, int, float, list[tuple]]:
    """Compute coverage stats for a list of journeys."""
    total = 0
    tested = 0
    partial = 0
    rows: list[tuple] = []
    for j in journeys:
        steps = j.get("steps", [])
        j_tested = sum(1 for s in steps if s.get("tested") is True)
        j_partial = sum(1 for s in steps if s.get("tested") == "partial")
        total += len(steps)
        tested += j_tested
        partial += j_partial
        cov = round(j_tested / len(steps) * 100, 1) if steps else 0
        rows.append((j.get("id", ""), j.get("name", ""), len(steps), j_tested, j_partial, cov))
    overall = round(tested / total * 100, 1) if total else 0
    return total, tested, partial, overall, rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("journeys_file", nargs="?", help="Path to journeys.json (auto-detected if omitted)")
    parser.add_argument("--output", default=None)
    parser.add_argument("--save-baseline", action="store_true",
                        help="Force-save current state as the baseline snapshot")
    parser.add_argument("--clear-baseline", action="store_true",
                        help="Remove baseline to start fresh")
    args = parser.parse_args()

    args.journeys_file = args.journeys_file or find_journeys_file() or "pathfinder/journeys.json"

    # Default output: same directory as journeys file
    if args.output is None:
        args.output = os.path.join(os.path.dirname(args.journeys_file) or '.', 'blazes.md')

    try:
        with open(args.journeys_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {args.journeys_file}", file=sys.stderr)
        print("Run /map first to create journeys.json", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {args.journeys_file}: {e}", file=sys.stderr)
        print("Check the file for syntax errors or run /map to regenerate", file=sys.stderr)
        sys.exit(1)

    journeys = data.get("journeys", [])
    if not journeys:
        print("ERROR: No journeys found", file=sys.stderr)
        sys.exit(1)

    # Validate journey structure before processing
    validate_journey_structure(journeys)

    # ── Baseline management ──
    baseline_path = os.path.join(os.path.dirname(args.journeys_file), "journeys-baseline.json")

    if args.clear_baseline and os.path.exists(baseline_path):
        os.remove(baseline_path)
        print(f"Cleared baseline: {baseline_path}")

    baseline_journeys = None
    if os.path.exists(baseline_path) and not args.save_baseline:
        try:
            with open(baseline_path) as f:
                baseline_data = json.load(f)
            baseline_journeys = baseline_data.get("journeys", [])
        except json.JSONDecodeError as e:
            print(f"WARNING: Corrupt baseline JSON in {baseline_path}: {e}", file=sys.stderr)
            baseline_journeys = None

    if args.save_baseline or not os.path.exists(baseline_path):
        # Save current state as baseline
        import shutil
        shutil.copy2(args.journeys_file, baseline_path)
        print(f"Baseline saved: {baseline_path}")

    lines = ["# Pathfinder Coverage Map\n"]
    total_steps, total_tested, total_partial, overall, summary_rows = compute_coverage(journeys)

    # ── Legend ──
    lines.append("### Legend\n")
    lines.append("| Symbol | Meaning |")
    lines.append("|--------|---------|")
    lines.append("| 🟢 ✅ | **Tested** — step has a passing UI test |")
    lines.append("| 🟡 ⚠️ | **Partial** — test written but disabled or implicitly covered |")
    lines.append("| 🔴 ❌ | **Untested** — no UI test coverage |")
    lines.append("| 🔵 🔀 | **Decision point** — user chooses between paths |")
    lines.append("| ⚡ | **Error path** — API failure branch |")
    lines.append("| `──▶` | Same-screen transition |")
    lines.append("| `╌╌▶` | Cross-screen navigation |\n")

    # ── Before / After comparison ──
    if baseline_journeys is not None:
        b_total, b_tested, b_partial, b_overall, b_rows = compute_coverage(baseline_journeys)

        # Only show before/after if coverage actually changed
        if b_overall != overall or b_tested != total_tested:
            lines.append("## 📸 Before (Baseline)\n")
            lines.append(f"**Coverage: {b_tested}/{b_total} steps tested ({b_overall}%)**\n")
            lines.append("```mermaid")
            lines.extend(build_decision_tree(baseline_journeys))
            lines.append("```\n")

            lines.append("## 🚀 After (Current)\n")
            lines.append(f"**Coverage: {total_tested}/{total_steps} steps tested ({overall}%)**\n")
            lines.append("```mermaid")
            lines.extend(build_decision_tree(journeys))
            lines.append("```\n")

            # Delta summary
            delta_tested = total_tested - b_tested
            delta_overall = round(overall - b_overall, 1)
            sign = "+" if delta_tested >= 0 else ""
            sign_pct = "+" if delta_overall >= 0 else ""
            lines.append("### 📊 Coverage Delta\n")
            lines.append("| Metric | Before | After | Delta |")
            lines.append("|--------|--------|-------|-------|")
            lines.append(
                f"| Steps tested | {b_tested}/{b_total}"
                f" | {total_tested}/{total_steps}"
                f" | {sign}{delta_tested} |"
            )
            lines.append(f"| Coverage | {b_overall}% | {overall}% | {sign_pct}{delta_overall}% |")

            # Per-journey delta
            b_lookup = {r[0]: r for r in b_rows}
            lines.append("")
            lines.append("| Journey | Before | After | Delta |")
            lines.append("|---------|--------|-------|-------|")
            for jid, jname, _j_steps, j_tested, _j_partial, j_cov in summary_rows:
                icon = get_icon(jname)
                if jid in b_lookup:
                    _, _, _, bj_tested, _, bj_cov = b_lookup[jid]
                    d = j_tested - bj_tested
                    d_sign = "+" if d >= 0 else ""
                    lines.append(f"| {icon} {jname} | {bj_cov}% | {j_cov}% | {d_sign}{d} steps |")
                else:
                    lines.append(f"| {icon} {jname} | — | {j_cov}% | new |")
            lines.append("")
        else:
            # No change — just show current tree
            lines.append("## 🌳 Decision Tree — All Paths\n")
            lines.append("```mermaid")
            lines.extend(build_decision_tree(journeys))
            lines.append("```\n")
    else:
        # No baseline — just show current tree
        lines.append("## 🌳 Decision Tree — All Paths\n")
        lines.append("```mermaid")
        lines.extend(build_decision_tree(journeys))
        lines.append("```\n")

    # ── Per-journey flowcharts ──
    for journey in journeys:
        jname = journey["name"]
        icon = get_icon(jname)
        lines.append(f"## {icon} {jname}\n")
        lines.append("```mermaid")
        lines.extend(build_journey_flowchart(journey, journeys))
        lines.append("```\n")

    # Insert overall coverage after title
    lines.insert(1, f"**Coverage: {total_tested}/{total_steps} steps tested ({overall}%)**\n")

    # Summary table
    lines.append("## Summary\n")
    lines.append("| Journey | Steps | Tested | Coverage |")
    lines.append("|---------|-------|--------|----------|")
    for (_jid, jname, step_count,
         tested_count, _partial_count, cov) in summary_rows:
        icon = get_icon(jname)
        bar = "🟢" if cov >= 80 else "🟡" if cov >= 50 else "🔴"
        lines.append(f"| {icon} {jname} | {step_count} | {tested_count} | {bar} {cov}% |")
    lines.append(f"| **Total** | **{total_steps}** | **{total_tested}** | **{overall}%** |")

    output = "\n".join(lines) + "\n"

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        f.write(output)

    print(f"Generated: {args.output}")
    print(f"Coverage: {total_tested}/{total_steps} ({overall}%)")

    summary = {
        "totalSteps": total_steps,
        "tested": total_tested,
        "untested": total_steps - total_tested,
        "coverage": overall,
        "journeys": len(journeys),
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
