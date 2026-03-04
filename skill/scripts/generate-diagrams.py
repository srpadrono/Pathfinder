#!/usr/bin/env python3
"""Generate Mermaid flowchart diagrams from journeys.json.

Usage: python3 generate-diagrams.py .pathfinder/journeys.json [--output .pathfinder/blazes.md]
"""
import json, sys, os, argparse, re


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
    return text.replace("(", "[").replace(")", "]")


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("journeys_file", help="Path to journeys.json")
    parser.add_argument("--output", default=".pathfinder/blazes.md")
    args = parser.parse_args()

    with open(args.journeys_file) as f:
        data = json.load(f)

    journeys = data.get("journeys", [])
    if not journeys:
        print("ERROR: No journeys found", file=sys.stderr)
        sys.exit(1)

    lines = ["# Pathfinder Coverage Map\n"]
    total_steps = 0
    total_tested = 0
    summary_rows = []

    for journey in journeys:
        jname = journey["name"]
        icon = get_icon(jname)
        steps = journey.get("steps", [])

        tested = sum(1 for s in steps if s.get("tested") is True)
        total_steps += len(steps)
        total_tested += tested

        coverage = round(tested / len(steps) * 100, 1) if steps else 0
        summary_rows.append((f"{icon} {jname}", len(steps), tested, coverage))

        lines.append(f"## {icon} {jname}\n")
        lines.append("```mermaid")
        lines.extend(build_flowchart(journey))
        lines.append("```\n")

    # Insert overall coverage after title
    overall = round(total_tested / total_steps * 100, 1) if total_steps else 0
    lines.insert(1, f"**Coverage: {total_tested}/{total_steps} steps tested ({overall}%)**\n")

    # Summary table
    lines.append("## Summary\n")
    lines.append("| Journey | Steps | Tested | Coverage |")
    lines.append("|---------|-------|--------|----------|")
    for name, step_count, tested_count, cov in summary_rows:
        bar = "🟢" if cov >= 80 else "🟡" if cov >= 50 else "🔴"
        lines.append(f"| {name} | {step_count} | {tested_count} | {bar} {cov}% |")
    lines.append(f"| **Total** | **{total_steps}** | **{total_tested}** | **{overall}%** |")

    output = "\n".join(lines) + "\n"

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
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
