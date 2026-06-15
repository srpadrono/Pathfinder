#!/usr/bin/env python3
"""Validate the eval datasets — schema + best-practice structural rules.

Runs with no model and no network, so CI can gate every PR on a well-formed,
non-degenerate eval suite. Exits non-zero on any violation.

Checks (beyond JSON Schema):
  * >= 3 output-quality cases, each with >= 2 expectations and >= 1 discriminating one.
  * unique case ids and expectation ids.
  * every referenced fixture file exists.
  * >= 16 triggering queries, with both classes well represented (>= 6 each).
  * unique trigger ids.

Usage: python3 validate_suite.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from _common import EVALS_DIR, load_json

try:
    import jsonschema  # type: ignore
    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False


def _schema_validate(data: dict, schema_path: Path, errors: list[str]) -> None:
    if not HAVE_JSONSCHEMA:
        return
    schema = load_json(schema_path)
    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.path) or "<root>"
        errors.append(f"schema: {loc}: {err.message}")


def validate_output_quality(errors: list[str], warnings: list[str]) -> None:
    path = EVALS_DIR / "output_quality.json"
    data = load_json(path)
    _schema_validate(data, EVALS_DIR / "schema" / "output-quality.schema.json", errors)

    cases = data.get("evals", [])
    if len(cases) < 3:
        errors.append(f"output_quality: need >= 3 cases, found {len(cases)}")

    seen_ids: set[str] = set()
    for case in cases:
        cid = case.get("id", "<missing>")
        if cid in seen_ids:
            errors.append(f"output_quality: duplicate case id '{cid}'")
        seen_ids.add(cid)

        exps = case.get("expectations", [])
        if len(exps) < 2:
            errors.append(f"output_quality[{cid}]: need >= 2 expectations, found {len(exps)}")
        if not any(e.get("discriminating") for e in exps):
            errors.append(
                f"output_quality[{cid}]: at least one expectation must be discriminating:true "
                "(would fail for a clearly-wrong output)"
            )
        seen_exp: set[str] = set()
        for e in exps:
            eid = e.get("id", "<missing>")
            if eid in seen_exp:
                errors.append(f"output_quality[{cid}]: duplicate expectation id '{eid}'")
            seen_exp.add(eid)

        for mapping in case.get("files", []):
            src = EVALS_DIR / mapping.get("from", "")
            if not src.exists():
                errors.append(f"output_quality[{cid}]: fixture not found: {mapping.get('from')}")


def validate_triggering(errors: list[str], warnings: list[str]) -> None:
    path = EVALS_DIR / "triggering.json"
    data = load_json(path)
    _schema_validate(data, EVALS_DIR / "schema" / "triggering.schema.json", errors)

    queries = data.get("queries", [])
    if len(queries) < 16:
        errors.append(f"triggering: need >= 16 queries, found {len(queries)}")

    positives = [q for q in queries if q.get("should_trigger") is True]
    negatives = [q for q in queries if q.get("should_trigger") is False]
    if len(positives) < 6:
        errors.append(f"triggering: need >= 6 should-trigger queries, found {len(positives)}")
    if len(negatives) < 6:
        errors.append(
            f"triggering: need >= 6 should-NOT-trigger near-misses, found {len(negatives)}"
        )

    seen: set[str] = set()
    for q in queries:
        qid = q.get("id", "<missing>")
        if qid in seen:
            errors.append(f"triggering: duplicate query id '{qid}'")
        seen.add(qid)
        if q.get("should_trigger") is False and not q.get("rationale"):
            warnings.append(f"triggering[{qid}]: negative query has no rationale (why is it a near-miss?)")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not HAVE_JSONSCHEMA:
        warnings.append(
            "jsonschema not installed — running structural checks only. "
            "Install with: pip install jsonschema"
        )

    validate_output_quality(errors, warnings)
    validate_triggering(errors, warnings)

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"\n✘ Eval suite invalid: {len(errors)} error(s).", file=sys.stderr)
        return 1

    print("✓ Eval suite valid (schema + structural checks passed).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
