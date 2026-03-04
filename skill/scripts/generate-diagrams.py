#!/usr/bin/env python3
"""Generate Mermaid journey diagrams from journeys.json.

Usage: python3 generate-diagrams.py .pathfinder/journeys.json [--output .pathfinder/blazes.md]
"""
import json, sys, os, argparse

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
        jid = journey["id"]
        jname = journey["name"]
        icon = get_icon(jname)
        steps = journey.get("steps", [])

        tested = sum(1 for s in steps if s.get("tested") is True)
        partial = sum(1 for s in steps if s.get("tested") == "partial")
        total_steps += len(steps)
        total_tested += tested

        coverage = round(tested / len(steps) * 100, 1) if steps else 0
        summary_rows.append((f"{icon} {jname}", len(steps), tested, coverage))

        # Generate Mermaid journey diagram
        lines.append(f"## {icon} {jname}\n")
        lines.append("```mermaid")
        lines.append("journey")
        lines.append(f"    title {icon} {jname}")

        # Group steps by screen/section
        current_section = None
        for step in steps:
            screen = step.get("screen", "Main")
            if screen != current_section:
                current_section = screen
                lines.append(f"    section {screen}")

            if step.get("tested") is True:
                score = 5
                marker = "✅"
            elif step.get("tested") == "partial":
                score = 4
                marker = "⚠️"
            else:
                score = 3
                marker = "❌"

            action = step.get("action", step.get("id", "?"))
            lines.append(f"      {action}: {score}: {marker}")

        lines.append("```\n")

    # Coverage summary
    overall = round(total_tested / total_steps * 100, 1) if total_steps else 0
    lines.insert(1, f"**Coverage: {total_tested}/{total_steps} steps tested ({overall}%)**\n")

    lines.append("## Summary\n")
    lines.append("| Journey | Steps | Tested | Coverage |")
    lines.append("|---------|-------|--------|----------|")
    for name, steps, tested, cov in summary_rows:
        bar = "🟢" if cov >= 80 else "🟡" if cov >= 50 else "🔴"
        lines.append(f"| {name} | {steps} | {tested} | {bar} {cov}% |")
    lines.append(f"| **Total** | **{total_steps}** | **{total_tested}** | **{overall}%** |")

    output = "\n".join(lines) + "\n"

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        f.write(output)

    print(f"Generated: {args.output}")
    print(f"Coverage: {total_tested}/{total_steps} ({overall}%)")

    # Also output JSON summary
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
