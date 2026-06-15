#!/usr/bin/env python3
"""Aggregate graded eval runs into a benchmark with variance and A/B analysis.

Reports, per case and overall:
  * mean +/- stddev pass rate across runs (variance),
  * the with_skill - without_skill delta (does the skill actually help?),
  * non-discriminating assertions (pass equally with and without the skill — they
    don't measure skill value), and
  * high-variance / possibly-flaky cases.

The interesting math lives in pure functions (compute_benchmark, analyze_*) so it
is unit-tested without a model. Reads a run dir produced by run_evals.py +
grade_evals.py; writes benchmark.json and benchmark.md.

Usage: python3 aggregate_benchmark.py --run-dir evals/runs/<timestamp>
"""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

from _common import EVALS_DIR, RUNS_DIR, load_json, write_json


def _mean(xs: list[float]) -> float:
    return round(statistics.mean(xs), 3) if xs else 0.0


def _stddev(xs: list[float]) -> float:
    return round(statistics.stdev(xs), 3) if len(xs) > 1 else 0.0


def collect_records(run_dir: Path) -> tuple[list[dict], int]:
    """Return (records, ungraded_count). One record per *successfully graded* run.

    Runs whose grading has no expectations (e.g. the judge was unavailable) are NOT
    counted as 0% — they're skipped and reported separately, so a model outage never
    masquerades as a skill failure."""
    records: list[dict] = []
    ungraded = 0
    for grading_path in sorted(run_dir.rglob("grading.json")):
        grading = load_json(grading_path)
        if not grading.get("expectations"):
            ungraded += 1
            continue
        transcript = load_json(grading_path.parent / "transcript.json")
        timing_path = grading_path.parent / "timing.json"
        timing = load_json(timing_path) if timing_path.exists() else {}
        records.append({
            "eval_id": transcript["eval_id"],
            "config": transcript["config"],
            "run": transcript["run"],
            "pass_rate": grading.get("summary", {}).get("pass_rate", 0.0),
            "expectations": [
                {"id": e.get("id"), "passed": bool(e.get("passed"))}
                for e in grading.get("expectations", [])
            ],
            "duration_ms": timing.get("duration_ms"),
        })
    return records, ungraded


def compute_benchmark(records: list[dict], declared: dict | None = None) -> dict:
    """Pure aggregation. See module docstring.

    ``declared`` optionally maps (eval_id, expectation_id) -> bool (the case author's
    ``discriminating`` claim); when given, the result reconciles it against observed data."""
    cases = sorted({r["eval_id"] for r in records})
    configs = sorted({r["config"] for r in records})

    per_case = []
    for cid in cases:
        entry: dict = {"eval_id": cid, "configs": {}}
        for cfg in configs:
            rates = [r["pass_rate"] for r in records if r["eval_id"] == cid and r["config"] == cfg]
            durs = [r["duration_ms"] for r in records
                    if r["eval_id"] == cid and r["config"] == cfg and r["duration_ms"] is not None]
            entry["configs"][cfg] = {
                "runs": len(rates),
                "mean_pass_rate": _mean(rates),
                "stddev_pass_rate": _stddev(rates),
                "mean_duration_ms": _mean(durs) if durs else None,
            }
        if "with_skill" in entry["configs"] and "without_skill" in entry["configs"]:
            entry["delta_pass_rate"] = round(
                entry["configs"]["with_skill"]["mean_pass_rate"]
                - entry["configs"]["without_skill"]["mean_pass_rate"], 3)
        per_case.append(entry)

    overall = {}
    for cfg in configs:
        case_means = [c["configs"][cfg]["mean_pass_rate"] for c in per_case if cfg in c["configs"]]
        overall[cfg] = {"mean_pass_rate": _mean(case_means)}
    if "with_skill" in overall and "without_skill" in overall:
        overall["delta_pass_rate"] = round(
            overall["with_skill"]["mean_pass_rate"] - overall["without_skill"]["mean_pass_rate"], 3)

    return {
        "configs": configs,
        "overall": overall,
        "per_case": per_case,
        "non_discriminating": analyze_non_discriminating(records),
        "high_variance": analyze_variance(per_case),
        "declared_mismatches": analyze_declared_discrimination(records, declared or {}),
    }


def _pair_rates(records: list[dict], threshold: float = 0.25) -> dict:
    """{(eval_id, exp_id): {with, without, discriminates}} for pairs present in both arms."""
    keys = {(r["eval_id"], e["id"]) for r in records for e in r["expectations"]}
    out = {}
    for eid, exp_id in keys:
        def rate(cfg: str, eid: str = eid, exp_id: str = exp_id) -> float | None:
            vals = [1.0 if e["passed"] else 0.0
                    for r in records if r["eval_id"] == eid and r["config"] == cfg
                    for e in r["expectations"] if e["id"] == exp_id]
            return _mean(vals) if vals else None
        w, wo = rate("with_skill"), rate("without_skill")
        if w is not None and wo is not None:
            out[(eid, exp_id)] = {"with_skill": w, "without_skill": wo,
                                  "discriminates": abs(w - wo) >= threshold}
    return out


def analyze_declared_discrimination(records: list[dict], declared: dict,
                                    threshold: float = 0.25) -> list[dict]:
    """Reconcile each expectation's declared `discriminating` flag with observed data.

    Flags two kinds of mismatch: declared discriminating but it didn't, and it
    discriminated but was declared non-discriminating."""
    if not declared:
        return []
    mismatches = []
    for key, r in sorted(_pair_rates(records, threshold).items()):
        flag = declared.get(key)
        if flag is None:
            continue
        if flag and not r["discriminates"]:
            kind = "declared discriminating but did not (passes about equally in both arms)"
        elif (not flag) and r["discriminates"]:
            kind = "discriminated despite being declared non-discriminating"
        else:
            continue
        mismatches.append({"eval_id": key[0], "expectation_id": key[1], "declared": flag,
                           "with_skill": r["with_skill"], "without_skill": r["without_skill"],
                           "note": kind})
    return mismatches


def analyze_non_discriminating(records: list[dict], threshold: float = 0.25) -> list[dict]:
    """Expectations that pass at ~the same rate with and without the skill don't
    measure skill value. Flag them so the suite can be sharpened."""
    keys = {(r["eval_id"], e["id"]) for r in records for e in r["expectations"]}
    flags = []
    for eid, exp_id in sorted(keys):
        def rate(cfg: str, eid: str = eid, exp_id: str = exp_id) -> float | None:
            vals = [1.0 if e["passed"] else 0.0
                    for r in records if r["eval_id"] == eid and r["config"] == cfg
                    for e in r["expectations"] if e["id"] == exp_id]
            return _mean(vals) if vals else None
        w, wo = rate("with_skill"), rate("without_skill")
        if w is not None and wo is not None and abs(w - wo) < threshold:
            flags.append({"eval_id": eid, "expectation_id": exp_id,
                          "with_skill": w, "without_skill": wo,
                          "note": "passes about equally with and without the skill — may not discriminate"})
    return flags


def analyze_variance(per_case: list[dict], threshold: float = 0.3) -> list[dict]:
    flags = []
    for c in per_case:
        for cfg, stats in c["configs"].items():
            if stats["stddev_pass_rate"] > threshold:
                flags.append({"eval_id": c["eval_id"], "config": cfg,
                              "stddev_pass_rate": stats["stddev_pass_rate"],
                              "note": "high run-to-run variance — possibly flaky"})
    return flags


def to_markdown(bench: dict) -> str:
    o = bench["overall"]
    lines = ["# Pathfinder Eval Benchmark", "", "## Overall pass rate (mean across cases)", ""]
    lines.append("| Configuration | Mean pass rate |")
    lines.append("|---------------|----------------|")
    for cfg in bench["configs"]:
        lines.append(f"| {cfg} | {o.get(cfg, {}).get('mean_pass_rate', 0.0):.0%} |")
    if "delta_pass_rate" in o:
        d = o["delta_pass_rate"]
        lines.append(f"| **with − without (skill lift)** | **{d:+.0%}** |")

    lines += ["", "## Per case (mean ± stddev across runs)", "",
              "| Case | with_skill | without_skill | lift |",
              "|------|-----------|---------------|------|"]
    for c in bench["per_case"]:
        w = c["configs"].get("with_skill", {})
        wo = c["configs"].get("without_skill", {})
        ws = f"{w.get('mean_pass_rate', 0):.0%} ± {w.get('stddev_pass_rate', 0):.0%}" if w else "—"
        wos = f"{wo.get('mean_pass_rate', 0):.0%} ± {wo.get('stddev_pass_rate', 0):.0%}" if wo else "—"
        lift = f"{c['delta_pass_rate']:+.0%}" if "delta_pass_rate" in c else "—"
        lines.append(f"| {c['eval_id']} | {ws} | {wos} | {lift} |")

    if bench["non_discriminating"]:
        lines += ["", "## ⚠️ Non-discriminating assertions", "",
                  "These pass about equally with and without the skill — sharpen or remove them:", ""]
        for f in bench["non_discriminating"]:
            lines.append(f"- `{f['eval_id']}/{f['expectation_id']}` — "
                         f"with {f['with_skill']:.0%} vs without {f['without_skill']:.0%}")
    if bench["high_variance"]:
        lines += ["", "## ⚠️ High-variance cases", ""]
        for f in bench["high_variance"]:
            lines.append(f"- `{f['eval_id']}` ({f['config']}) — stddev {f['stddev_pass_rate']:.0%}")
    if bench.get("declared_mismatches"):
        lines += ["", "## ⚠️ Declared-vs-observed discrimination mismatches", "",
                  "The case author's `discriminating` flag didn't match the data:", ""]
        for f in bench["declared_mismatches"]:
            lines.append(f"- `{f['eval_id']}/{f['expectation_id']}` (declared {f['declared']}) — "
                         f"with {f['with_skill']:.0%} vs without {f['without_skill']:.0%}: {f['note']}")
    lines += ["", "---", "*Generated by aggregate_benchmark.py*"]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate Pathfinder eval benchmark")
    parser.add_argument("--run-dir", help="Run dir (default: most recent)")
    args = parser.parse_args()

    if args.run_dir:
        run_dir = Path(args.run_dir)
    else:
        dirs = [d for d in RUNS_DIR.iterdir() if d.is_dir()] if RUNS_DIR.exists() else []
        run_dir = max(dirs, key=lambda d: d.stat().st_mtime) if dirs else None
    if not run_dir or not run_dir.exists():
        print("ERROR: no run dir found.", file=sys.stderr)
        return 1

    records, ungraded = collect_records(run_dir)
    if not records:
        msg = f"no graded runs in {run_dir}."
        if ungraded:
            msg += (f" {ungraded} run(s) were ungraded (judge unavailable / no parseable "
                    "output) — these are NOT counted as 0%. Re-grade with grade_evals.py.")
        print(f"ERROR: {msg}", file=sys.stderr)
        return 1
    if ungraded:
        print(f"WARNING: {ungraded} run(s) ungraded and excluded (judge unavailable?).",
              file=sys.stderr)

    # Load each case's declared `discriminating` flags so we can reconcile them with observed data.
    declared = {}
    suite_path = EVALS_DIR / "output_quality.json"
    if suite_path.exists():
        for case in load_json(suite_path).get("evals", []):
            for e in case.get("expectations", []):
                declared[(case["id"], e["id"])] = bool(e.get("discriminating"))

    bench = compute_benchmark(records, declared)
    bench["ungraded_runs"] = ungraded
    write_json(run_dir / "benchmark.json", bench)
    (run_dir / "benchmark.md").write_text(to_markdown(bench))

    o = bench["overall"]
    print(f"Benchmark written to {run_dir}/benchmark.md")
    if "delta_pass_rate" in o:
        print(f"  with_skill:    {o['with_skill']['mean_pass_rate']:.0%}")
        print(f"  without_skill: {o['without_skill']['mean_pass_rate']:.0%}")
        print(f"  skill lift:    {o['delta_pass_rate']:+.0%}")
    if bench["non_discriminating"]:
        print(f"  ⚠ {len(bench['non_discriminating'])} non-discriminating assertion(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
