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
    """Build a single Mermaid flowchart showing all journeys as a decision tree.

    Merges journeys that share common screens/actions into branch points
    rendered as diamond decision nodes.
    """
    lines = ["flowchart TD"]
    styles = []
    declared = set()

    # Collect all steps with unique node IDs
    all_steps = {}
    for journey in journeys:
        for step in journey.get("steps", []):
            sid = sanitize_id(step["id"])
            all_steps[sid] = step

    # ── Build a tree structure by analysing the journeys ──
    # We look for shared first-step screens and merge them.
    # Group journeys by first screen to find the root.
    screen_groups = {}
    for journey in journeys:
        steps = journey.get("steps", [])
        if not steps:
            continue
        first_screen = steps[0].get("screen", "Main")
        screen_groups.setdefault(first_screen, []).append(journey)

    def declare_step(step, prefix=""):
        """Declare a step node if not already declared."""
        sid = sanitize_id(step["id"])
        if sid in declared:
            return sid
        declared.add(sid)
        is_tested, is_partial, marker = step_status(step)
        label = sanitize_label(f"{marker} {step.get('action', sid)}")
        lines.append(node_declaration(sid, label, is_tested, is_partial))
        styles.append(style_line(sid, step))
        return sid

    def add_decision(parent_id, label):
        """Add a diamond decision node with labelled branches."""
        decision_id = f"{parent_id}_decision"
        if decision_id not in declared:
            declared.add(decision_id)
            safe_label = sanitize_label(label)
            lines.append(f'    {decision_id}{{{{"🔀 {safe_label}"}}}}')
            styles.append(f"    style {decision_id} fill:#1f6feb,stroke:#1158c7,color:#fff")
        lines.append(f"    {parent_id} --> {decision_id}")
        return decision_id

    def emit_chain(steps, start_idx=0):
        """Emit a linear chain of steps, returning the last node id."""
        prev_id = None
        for i in range(start_idx, len(steps)):
            step = steps[i]
            sid = declare_step(step)
            if prev_id and sid not in declared_edges:
                prev_screen = steps[i - 1].get("screen", "Main") if i > start_idx else ""
                curr_screen = step.get("screen", "Main")
                arrow = " -.-> " if prev_screen != curr_screen else " --> "
                edge = f"    {prev_id}{arrow}{sid}"
                if edge not in declared_edges:
                    lines.append(edge)
                    declared_edges.add(edge)
            prev_id = sid
        return prev_id

    declared_edges = set()

    # ── Identify the main happy-path journeys (non-error) and error journeys ──
    main_journeys = [j for j in journeys if j.get("id", "").upper() != "ERROR"]
    error_journeys = [j for j in journeys if j.get("id", "").upper() == "ERROR"]

    # ── Find shared prefix among main journeys ──
    # Step 1: Declare the shared entry point
    if main_journeys:
        # All main journeys start with "User sees transaction details" on the same screen
        first_step = main_journeys[0]["steps"][0]
        root_id = declare_step(first_step)

        # ── Group by the second step action (the user's first decision) ──
        # Find branches: steps that diverge from the shared root
        branch_groups = {}
        for journey in main_journeys:
            steps = journey.get("steps", [])
            if len(steps) < 2:
                continue
            # Group by action text to merge journeys with same user action
            branch_key = steps[1].get("action", steps[1]["id"])
            branch_groups.setdefault(branch_key, []).append(journey)

        if len(branch_groups) > 1:
            # Multiple branches from root → decision point
            decision_id = add_decision(root_id, "User action?")

            for branch_key, branch_journeys in branch_groups.items():
                first_branch_step = branch_journeys[0]["steps"][1]
                branch_label = first_branch_step.get("action", branch_key)

                # Find where these sub-branches diverge
                if len(branch_journeys) == 1:
                    # Single path from here
                    journey = branch_journeys[0]
                    steps = journey["steps"]
                    first_sid = declare_step(steps[1])
                    edge = f'    {decision_id} -->|"{sanitize_label(branch_label)}"| {first_sid}'
                    if edge not in declared_edges:
                        lines.append(edge)
                        declared_edges.add(edge)
                    # Emit rest of chain
                    prev_id = first_sid
                    for k in range(2, len(steps)):
                        step = steps[k]
                        sid = declare_step(step)
                        prev_screen = steps[k - 1].get("screen", "Main")
                        curr_screen = step.get("screen", "Main")
                        arrow = " -.-> " if prev_screen != curr_screen else " --> "
                        edge = f"    {prev_id}{arrow}{sid}"
                        if edge not in declared_edges:
                            lines.append(edge)
                            declared_edges.add(edge)
                        prev_id = sid
                else:
                    # Multiple journeys share this branch → find their shared prefix
                    # then add another decision point
                    # Find common prefix length by comparing step actions
                    ref_steps = branch_journeys[0]["steps"]
                    common_len = len(ref_steps)
                    for bj in branch_journeys[1:]:
                        bj_steps = bj["steps"]
                        prefix_end = min(len(ref_steps), len(bj_steps))
                        for ci in range(1, prefix_end):
                            if ref_steps[ci].get("action") != bj_steps[ci].get("action"):
                                common_len = min(common_len, ci)
                                break

                    # Emit shared prefix
                    shared_step = ref_steps[1]
                    first_sid = declare_step(shared_step)
                    edge = f'    {decision_id} -->|"{sanitize_label(branch_label)}"| {first_sid}'
                    if edge not in declared_edges:
                        lines.append(edge)
                        declared_edges.add(edge)

                    prev_id = first_sid
                    for ci in range(2, common_len):
                        step = ref_steps[ci]
                        sid = declare_step(step)
                        prev_screen = ref_steps[ci - 1].get("screen", "Main")
                        curr_screen = step.get("screen", "Main")
                        arrow = " -.-> " if prev_screen != curr_screen else " --> "
                        edge = f"    {prev_id}{arrow}{sid}"
                        if edge not in declared_edges:
                            lines.append(edge)
                            declared_edges.add(edge)
                        prev_id = sid

                    # Sub-decision point
                    _sub_decision_label = ref_steps[common_len - 1].get("action", "Choice?") if common_len > 1 else "Choice?"
                    sub_decision_id = add_decision(prev_id, "User response?")

                    for bj in branch_journeys:
                        bj_steps = bj["steps"]
                        if common_len < len(bj_steps):
                            sub_step = bj_steps[common_len]
                            sub_sid = declare_step(sub_step)
                            sub_label = sub_step.get("action", sub_step["id"])
                            edge = f'    {sub_decision_id} -->|"{sanitize_label(sub_label)}"| {sub_sid}'
                            if edge not in declared_edges:
                                lines.append(edge)
                                declared_edges.add(edge)
                            sub_prev = sub_sid
                            for si in range(common_len + 1, len(bj_steps)):
                                step = bj_steps[si]
                                sid = declare_step(step)
                                prev_screen = bj_steps[si - 1].get("screen", "Main")
                                curr_screen = step.get("screen", "Main")
                                arrow = " -.-> " if prev_screen != curr_screen else " --> "
                                edge = f"    {sub_prev}{arrow}{sid}"
                                if edge not in declared_edges:
                                    lines.append(edge)
                                    declared_edges.add(edge)
                                sub_prev = sid
        else:
            # Single path, no branching
            journey = main_journeys[0]
            emit_chain(journey["steps"])

    # ── Error journeys: attach error steps to the loading/API steps they branch from ──
    for ej in error_journeys:
        steps = ej.get("steps", [])
        if not steps:
            continue
        # Group error steps by screen, then attach each group to
        # the matching loading/API step on that screen
        screen_groups_err = {}
        for step in steps:
            screen = step.get("screen", "Main")
            screen_groups_err.setdefault(screen, []).append(step)

        for screen, err_steps in screen_groups_err.items():
            # Find the loading/API step on this screen to branch from
            parent_id = None
            for mj in main_journeys:
                for ms in mj.get("steps", []):
                    ms_screen = ms.get("screen", "Main")
                    ms_action = ms.get("action", "").lower()
                    if ms_screen == screen and ("loading" in ms_action or "api" in ms_action):
                        candidate = sanitize_id(ms["id"])
                        if candidate in declared:
                            parent_id = candidate
                            break
                if parent_id:
                    break

            # Chain error steps for this screen
            prev_id = parent_id
            for step in err_steps:
                sid = declare_step(step)
                if prev_id:
                    if prev_id == parent_id:
                        edge = f'    {prev_id} -.->|"⚡ API Error"| {sid}'
                    else:
                        edge = f"    {prev_id} --> {sid}"
                    if edge not in declared_edges:
                        lines.append(edge)
                        declared_edges.add(edge)
                prev_id = sid

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
    parser.add_argument("journeys_file", help="Path to journeys.json")
    parser.add_argument("--output", default=None)
    parser.add_argument("--save-baseline", action="store_true",
                        help="Force-save current state as the baseline snapshot")
    parser.add_argument("--clear-baseline", action="store_true",
                        help="Remove baseline to start fresh")
    args = parser.parse_args()

    # Default output: same directory as journeys file
    if args.output is None:
        args.output = os.path.join(os.path.dirname(args.journeys_file) or '.', 'blazes.md')

    with open(args.journeys_file) as f:
        data = json.load(f)

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
        with open(baseline_path) as f:
            baseline_data = json.load(f)
        baseline_journeys = baseline_data.get("journeys", [])

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
