#!/usr/bin/env python3
"""Generate Mermaid flowchart diagrams from journeys.json.

Usage: python3 generate-diagrams.py [<testDir>/pathfinder/journeys.json] [--output <testDir>/pathfinder/blazes.md]
"""
import json, sys, os, argparse, re
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


def get_icon(journey_name):
    name_lower = journey_name.lower()
    for key, icon in JOURNEY_ICONS.items():
        if key in name_lower:
            return icon
    return "📋"


def sanitize_id(text):
    """Create a safe Mermaid node id."""
    return re.sub(r"[^a-zA-Z0-9]", "_", text).strip("_")


def sanitize_label(text):
    """Escape characters that break Mermaid label parsing."""
    return text.replace("(", "[").replace(")", "]").replace('"', "'")


def step_status(step):
    """Return (is_tested, is_partial, marker) for a step."""
    is_tested = step.get("tested") is True
    is_partial = step.get("tested") == "partial"
    marker = "✅" if is_tested else "⚠️" if is_partial else "❌"
    return is_tested, is_partial, marker


def style_line(node_id, step):
    """Return the Mermaid style line for a node."""
    if step.get("tested") is True:
        return f"    style {node_id} fill:#2ea043,stroke:#1a7f37,color:#fff"
    elif step.get("tested") == "partial":
        return f"    style {node_id} fill:#d29922,stroke:#b87d14,color:#fff"
    else:
        return f"    style {node_id} fill:#f85149,stroke:#da3633,color:#fff"


def node_declaration(node_id, label, is_tested, is_partial):
    """Return the Mermaid node declaration."""
    quoted = f'"{label}"'
    if is_tested:
        return f"    {node_id}({quoted})"
    elif is_partial:
        return f"    {node_id}[/{quoted}/]"
    else:
        return f"    {node_id}[{quoted}]"


def build_decision_tree(journeys):
    """Build a single Mermaid flowchart showing all journeys as a graph."""
    lines = ["flowchart TD"]
    styles = []
    declared_nodes = set()
    declared_decisions = set()
    declared_edges = set()
    nodes = {}
    roots = []
    incoming = defaultdict(set)
    outgoing = defaultdict(list)
    edge_meta = {}

    for journey in journeys:
        steps = journey.get("steps", [])
        prev_id = None
        prev_screen = None
        for index, step in enumerate(steps):
            node_id = sanitize_id(step["id"])
            if node_id not in nodes:
                nodes[node_id] = step
            if index == 0 and node_id not in roots:
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
                    },
                )

            prev_id = node_id
            prev_screen = step.get("screen", "Main")

    def declare_step(node_id):
        if node_id in declared_nodes:
            return
        step = nodes[node_id]
        is_tested, is_partial, marker = step_status(step)
        label = sanitize_label(f"{marker} {step.get('action', node_id)}")
        lines.append(node_declaration(node_id, label, is_tested, is_partial))
        styles.append(style_line(node_id, step))
        declared_nodes.add(node_id)

    def declare_decision(source_id):
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

    walked = set()

    def walk(node_id):
        if node_id in walked:
            return
        walked.add(node_id)
        declare_step(node_id)

        children = outgoing.get(node_id, [])
        if len(children) > 1:
            decision_id = declare_decision(node_id)
            for child_id in children:
                declare_step(child_id)
                label = sanitize_label(edge_meta[(node_id, child_id)]["label"])
                edge = f'    {decision_id} -->|"{label}"| {child_id}'
                if edge not in declared_edges:
                    lines.append(edge)
                    declared_edges.add(edge)
                walk(child_id)
            return

        if len(children) == 1:
            child_id = children[0]
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

    lines.extend(styles)
    return lines


def build_flowchart(journey):
    """Build a Mermaid flowchart for one journey."""
    steps = journey.get("steps", [])
    if not steps:
        return []

    lines = []
    lines.append("flowchart TD")

    # Group steps by screen for subgraphs
    screens = {}
    node_ids = []

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
    for screen, nodes in screens.items():
        if len(screens) > 1:
            lines.append(f"    subgraph {screen}")
        for node_id, label, is_tested, is_partial in nodes:
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


def compute_coverage(journeys):
    """Compute coverage stats for a list of journeys."""
    total = 0
    tested = 0
    partial = 0
    rows = []
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


def main():
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
            lines.append(f"| Steps tested | {b_tested}/{b_total} | {total_tested}/{total_steps} | {sign}{delta_tested} |")
            lines.append(f"| Coverage | {b_overall}% | {overall}% | {sign_pct}{delta_overall}% |")

            # Per-journey delta
            b_lookup = {r[0]: r for r in b_rows}
            lines.append("")
            lines.append("| Journey | Before | After | Delta |")
            lines.append("|---------|--------|-------|-------|")
            for jid, jname, j_steps, j_tested, j_partial, j_cov in summary_rows:
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
        lines.extend(build_flowchart(journey))
        lines.append("```\n")

    # Insert overall coverage after title
    lines.insert(1, f"**Coverage: {total_tested}/{total_steps} steps tested ({overall}%)**\n")

    # Summary table
    lines.append("## Summary\n")
    lines.append("| Journey | Steps | Tested | Coverage |")
    lines.append("|---------|-------|--------|----------|")
    for jid, jname, step_count, tested_count, partial_count, cov in summary_rows:
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
