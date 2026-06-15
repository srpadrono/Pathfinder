#!/usr/bin/env python3
"""Tests for the eval harness pure logic (no model/network required).

These prove the harness is correct and *honest*: the aggregation reports real
deltas, the analyzer flags non-discriminating assertions, the triggering math
thresholds correctly, and our committed eval datasets pass validation.
"""
import json
import os
import subprocess
import sys

import pytest

EVALS_SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "evals", "scripts")
sys.path.insert(0, os.path.abspath(EVALS_SCRIPTS))

import _common as common  # noqa: E402
import aggregate_benchmark as agg  # noqa: E402
import grade_evals as grade  # noqa: E402
import run_loop as loop  # noqa: E402
import run_triggering as trig  # noqa: E402

# ── aggregate_benchmark ──────────────────────────────────────────────────

def _record(eval_id, config, run, exps):
    passed = sum(1 for _, p in exps if p)
    return {
        "eval_id": eval_id, "config": config, "run": run,
        "pass_rate": round(passed / len(exps), 3) if exps else 0.0,
        "expectations": [{"id": i, "passed": p} for i, p in exps],
        "duration_ms": 1000,
    }


def test_compute_benchmark_reports_skill_lift():
    # with_skill passes everything; without_skill fails everything.
    records = []
    for run in (1, 2, 3):
        records.append(_record("c1", "with_skill", run, [("a", True), ("b", True)]))
        records.append(_record("c1", "without_skill", run, [("a", False), ("b", False)]))
    bench = agg.compute_benchmark(records)
    assert bench["overall"]["with_skill"]["mean_pass_rate"] == 1.0
    assert bench["overall"]["without_skill"]["mean_pass_rate"] == 0.0
    assert bench["overall"]["delta_pass_rate"] == 1.0
    # 'a' passes with and fails without → discriminating → NOT flagged.
    assert bench["non_discriminating"] == []


def test_analyze_non_discriminating_flags_equal_assertions():
    # 'noise' passes in both configs → non-discriminating; 'real' discriminates.
    records = []
    for run in (1, 2, 3):
        records.append(_record("c1", "with_skill", run, [("real", True), ("noise", True)]))
        records.append(_record("c1", "without_skill", run, [("real", False), ("noise", True)]))
    flags = agg.analyze_non_discriminating(records)
    flagged = {f["expectation_id"] for f in flags}
    assert "noise" in flagged
    assert "real" not in flagged


def test_analyze_variance_flags_flaky():
    records = [
        _record("c1", "with_skill", 1, [("a", True), ("b", True)]),   # 1.0
        _record("c1", "with_skill", 2, [("a", False), ("b", False)]),  # 0.0
        _record("c1", "with_skill", 3, [("a", True), ("b", False)]),   # 0.5
    ]
    bench = agg.compute_benchmark(records)
    assert any(f["eval_id"] == "c1" for f in bench["high_variance"])


def test_benchmark_markdown_renders():
    records = [_record("c1", "with_skill", 1, [("a", True)]),
               _record("c1", "without_skill", 1, [("a", False)])]
    md = agg.to_markdown(agg.compute_benchmark(records))
    assert "Pathfinder Eval Benchmark" in md
    assert "skill lift" in md


def test_declared_discrimination_reconciliation():
    # foo: declared discriminating but passes equally (didn't) -> mismatch
    # bar: declared non-discriminating but discriminates -> mismatch
    # baz: declared discriminating and discriminates -> no mismatch
    records = []
    for run in (1, 2, 3):
        records.append(_record("c1", "with_skill", run, [("foo", True), ("bar", True), ("baz", True)]))
        records.append(_record("c1", "without_skill", run, [("foo", True), ("bar", False), ("baz", False)]))
    declared = {("c1", "foo"): True, ("c1", "bar"): False, ("c1", "baz"): True}
    bench = agg.compute_benchmark(records, declared)
    flagged = {m["expectation_id"] for m in bench["declared_mismatches"]}
    assert flagged == {"foo", "bar"}, flagged
    # without declared flags, no reconciliation is attempted
    assert agg.compute_benchmark(records)["declared_mismatches"] == []


# ── run_triggering ───────────────────────────────────────────────────────

def test_trigger_rate():
    assert trig.trigger_rate([True, True, False]) == pytest.approx(0.667, abs=0.01)
    assert trig.trigger_rate([]) == 0.0


def test_query_passed_thresholds():
    assert trig.query_passed(True, 0.67) is True
    assert trig.query_passed(True, 0.33) is False
    assert trig.query_passed(False, 0.33) is True   # stayed quiet enough
    assert trig.query_passed(False, 0.67) is False   # over-triggered


def test_split_is_stratified_and_deterministic():
    queries = [{"id": f"p{i}", "should_trigger": True} for i in range(10)]
    queries += [{"id": f"n{i}", "should_trigger": False} for i in range(10)]
    train, test = trig.split_train_test(queries, train_frac=0.6)
    assert trig.split_train_test(queries) == trig.split_train_test(queries)  # deterministic
    # stratified: both classes present in train and test
    assert any(q["should_trigger"] for q in test) and any(not q["should_trigger"] for q in test)
    assert len(train) + len(test) == 20


def test_metrics_confusion():
    results = [
        {"should_trigger": True, "fired": True, "passed": True},
        {"should_trigger": True, "fired": False, "passed": False},
        {"should_trigger": False, "fired": False, "passed": True},
        {"should_trigger": False, "fired": True, "passed": False},
    ]
    m = trig.metrics(results)
    assert m["confusion"] == {"tp": 1, "fp": 1, "tn": 1, "fn": 1}
    assert m["accuracy"] == 0.5
    assert m["precision"] == 0.5
    assert m["recall"] == 0.5


def test_detect_trigger_fires_on_namespaced_skill():
    for cmd in ("pathfinder", "pathfinder:pathfinder", "pathfinder:map"):
        ev = json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Skill", "input": {"command": cmd}}]}})
        assert trig.detect_trigger(ev, trig.SKILL_NAMES) is True, cmd


def test_detect_trigger_ignores_non_skill_tools():
    quiet = json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]}})
    assert trig.detect_trigger(quiet, trig.SKILL_NAMES) is False


def test_detect_trigger_no_false_positive_on_generic_words():
    """An UNRELATED skill whose args merely contain 'map'/'sitemap'/'scout' is NOT a
    Pathfinder trigger — the bug the harden review caught."""
    other = json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Skill",
         "input": {"command": "frontend-design", "arguments": "build a sitemap and scout layout"}}]}})
    assert trig.detect_trigger(other, trig.SKILL_NAMES) is False


# ── run_loop (description optimizer) ─────────────────────────────────────

def test_swap_description_replaces_frontmatter():
    md = '---\nname: pathfinder\ndescription: "old desc"\nallowed-tools: Bash\n---\n\n# Body\n'
    out = loop.swap_description(md, "new and improved description")
    assert 'description: "new and improved description"' in out
    assert "old desc" not in out
    assert "name: pathfinder" in out and "# Body" in out


def test_swap_description_escapes_quotes():
    md = '---\ndescription: x\n---\n'
    out = loop.swap_description(md, 'has "quotes" inside')
    assert "has 'quotes' inside" in out  # double quotes downgraded so YAML stays valid


def test_best_by_test_picks_highest_held_out_score():
    candidates = [
        {"description": "a", "train": {"accuracy": 0.9}, "test": {"accuracy": 0.6}},
        {"description": "b", "train": {"accuracy": 0.7}, "test": {"accuracy": 0.8}},
        {"description": "c", "train": {"accuracy": 1.0}, "test": {"accuracy": 0.8}},
    ]
    best = loop.best_by_test(candidates)
    # b and c tie on test (0.8); tie broken by train → c (1.0)
    assert best["description"] == "c"


# ── model-unavailability honesty (a limit must not look like a skill failure) ──

def test_model_unavailable_detection():
    assert common.model_unavailable("You've hit your session limit · resets 4:30am") is True
    assert common.model_unavailable("There's an issue with the selected model (x). It may not "
                                    "exist or you may not have access to it.") is True
    assert common.model_unavailable("Here is the journey map you asked for.") is False
    assert common.model_unavailable("") is False


def test_already_graded_resume_predicate(tmp_path):
    import json as _json
    p = tmp_path / "grading.json"
    assert grade.already_graded(p) is False                       # missing
    p.write_text(_json.dumps({"expectations": [], "error": "x"}))
    assert grade.already_graded(p) is False                       # ungraded (judge was down)
    p.write_text(_json.dumps({"expectations": [{"id": "a", "passed": True}]}))
    assert grade.already_graded(p) is True                        # has verdicts → skip on resume


def test_collect_records_skips_ungraded_runs(tmp_path):
    import json as _json

    def _run(cfg, run, grading):
        d = tmp_path / "case1" / cfg / f"run-{run}"
        d.mkdir(parents=True)
        (d / "grading.json").write_text(_json.dumps(grading))
        (d / "transcript.json").write_text(_json.dumps(
            {"eval_id": "case1", "config": cfg, "run": run}))
        (d / "timing.json").write_text(_json.dumps({"duration_ms": 10}))

    _run("with_skill", 1, {"expectations": [{"id": "a", "passed": True}],
                           "summary": {"pass_rate": 1.0}})
    # judge was unavailable here → empty expectations → must be skipped, not counted 0%
    _run("without_skill", 1, {"expectations": [], "error": "judge model unavailable"})

    records, ungraded = agg.collect_records(tmp_path)
    assert len(records) == 1
    assert ungraded == 1
    assert records[0]["config"] == "with_skill"


# ── dataset validation (runs against the REAL committed suite) ────────────

def test_committed_eval_suite_is_valid():
    r = subprocess.run([sys.executable, os.path.join(EVALS_SCRIPTS, "validate_suite.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"eval suite invalid:\n{r.stderr}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
