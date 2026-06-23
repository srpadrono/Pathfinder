#!/usr/bin/env python3
"""Optimize the skill's `description` against the triggering eval — the eval loop.

Modeled on skill-creator's run_loop.py. It splits the triggering queries into a
train and a held-out test set, scores the current description, asks a model to
propose an improved description from the *train* failures, re-scores candidates,
and keeps the best by **held-out test score** (so we don't overfit to the phrasings
we tuned against).

Needs the `claude` CLI logged in. The pure pieces (swap_description, best_by_test)
are unit-tested without a model.

Usage:
  python3 run_loop.py --max-iterations 3 --runs 1
  python3 run_loop.py --dry-run     # show the split + plan, no model calls
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

from _common import EVALS_DIR, SKILLS_DIR, build_plugin_dir, claude_flags, have_command, load_json
from run_triggering import metrics, run_query_once, split_train_test, trigger_rate

SKILL_MD = SKILLS_DIR / "pathfinder" / "SKILL.md"
DESC_RE = re.compile(r'^(description:\s*)(.*)$', re.MULTILINE)


def current_description() -> str:
    m = DESC_RE.search(SKILL_MD.read_text())
    if not m:
        return ""
    val = m.group(2).strip()
    if len(val) >= 2 and val[0] in "\"'" and val[-1] == val[0]:
        val = val[1:-1]
    return val


def swap_description(skill_md_text: str, new_desc: str) -> str:
    """Return SKILL.md text with the frontmatter description replaced (quoted)."""
    safe = new_desc.replace('"', "'")
    return DESC_RE.sub(lambda m: f'{m.group(1)}"{safe}"', skill_md_text, count=1)


def best_by_test(candidates: list[dict]) -> dict:
    """Pick the candidate with the highest held-out test accuracy (ties → train)."""
    return max(candidates, key=lambda c: (c["test"]["accuracy"], c["train"]["accuracy"]))


def _plugin_with_description(desc: str, dest: Path) -> Path:
    """Build a loadable plugin dir (--plugin-dir target) with the description swapped."""
    build_plugin_dir(dest)
    md = dest / "skills" / "pathfinder" / "SKILL.md"
    md.write_text(swap_description(md.read_text(), desc))
    return dest


def score(desc: str, queries: list[dict], runs: int, work: Path, model: str) -> dict:
    plugin_dir = _plugin_with_description(desc, work / "plugin")
    results = []
    for q in queries:
        rate = trigger_rate([run_query_once(q["query"], model=model, plugin_dir=plugin_dir)
                             for _ in range(runs)])
        results.append({"should_trigger": q["should_trigger"], "fired": rate >= 0.5,
                        "passed": (rate >= 0.5) == q["should_trigger"]})
    shutil.rmtree(plugin_dir, ignore_errors=True)
    return metrics(results)


def propose_description(current: str, train_failures: list[dict], model: str) -> str | None:
    import subprocess
    fails = "\n".join(
        f"- query: {f['query']!r} | should_trigger={f['should_trigger']} | observed_fired={f['fired']}"
        for f in train_failures)
    prompt = (
        "You are tuning the `description` of an Agent Skill so it triggers correctly. "
        "The skill maps UI user journeys, visualizes test coverage, and generates E2E tests. "
        "It must NOT trigger for unit tests, API tests, line-coverage, or flaky-test debugging.\n\n"
        f"Current description:\n{current}\n\n"
        f"Train-set mistakes to fix:\n{fails}\n\n"
        "Rules: third person; <=1024 chars; no angle brackets; say what it does AND when to use it; "
        "be slightly pushy against under-triggering but precise enough to avoid the near-misses above.\n"
        'Return ONLY JSON: {"description": "..."}')
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "json"] + claude_flags()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    try:
        text = json.loads(proc.stdout).get("result", proc.stdout)
        m = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(m.group(0))["description"] if m else None
    except (json.JSONDecodeError, KeyError, AttributeError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Optimize the skill description (triggering loop)")
    parser.add_argument("--max-iterations", type=int, default=3)
    parser.add_argument("--runs", type=int, default=1, help="Runs per query")
    parser.add_argument("--model", default="opus", help="Model that PROPOSES descriptions")
    parser.add_argument("--trigger-model", default="sonnet", help="Model used for the trigger runs")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    queries = load_json(EVALS_DIR / "triggering.json")["queries"]
    train, test = split_train_test(queries)
    print(f"Split: {len(train)} train / {len(test)} held-out test")

    if args.dry_run:
        print("Train ids:", [q["id"] for q in train])
        print("Test ids: ", [q["id"] for q in test])
        print("Current description:\n ", current_description())
        return 0

    if not have_command("claude"):
        print("ERROR: the optimizer loop needs the 'claude' CLI logged in.", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="pf-loop-") as tmp:
        work = Path(tmp)
        tm = args.trigger_model
        candidates = [{"description": current_description(),
                       "train": score(current_description(), train, args.runs, work / "c0-train", tm),
                       "test": score(current_description(), test, args.runs, work / "c0-test", tm)}]
        print(f"  baseline: test acc {candidates[0]['test']['accuracy']:.0%}")

        desc = candidates[0]["description"]
        for i in range(1, args.max_iterations + 1):
            train_results = []
            plugin_dir = _plugin_with_description(desc, work / f"i{i}-plugin")
            for q in train:
                rate = trigger_rate([run_query_once(q["query"], model=tm, plugin_dir=plugin_dir)
                                     for _ in range(args.runs)])
                train_results.append({**q, "fired": rate >= 0.5,
                                      "passed": (rate >= 0.5) == q["should_trigger"]})
            shutil.rmtree(plugin_dir, ignore_errors=True)
            failures = [r for r in train_results if not r["passed"]]
            if not failures:
                print(f"  iteration {i}: no train failures — stopping")
                break
            proposed = propose_description(desc, failures, args.model)
            if not proposed:
                print(f"  iteration {i}: model returned no candidate — stopping")
                break
            cand = {"description": proposed,
                    "train": score(proposed, train, args.runs, work / f"i{i}-train", tm),
                    "test": score(proposed, test, args.runs, work / f"i{i}-test", tm)}
            candidates.append(cand)
            print(f"  iteration {i}: test acc {cand['test']['accuracy']:.0%}")
            desc = proposed

    best = best_by_test(candidates)
    out = {"best_description": best["description"],
           "best_test_accuracy": best["test"]["accuracy"],
           "baseline_test_accuracy": candidates[0]["test"]["accuracy"]}
    print("\n" + json.dumps(out, indent=2))
    print("\nIf best_description differs and scores higher, update skills/pathfinder/SKILL.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
