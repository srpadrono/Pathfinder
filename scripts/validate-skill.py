#!/usr/bin/env python3
"""Validate SKILL.md frontmatter against the Agent Skills open standard.

Enforces the rules Anthropic's skill-creator validator enforces, so these skills
stay portable across Claude Code, the Claude API, and Codex:

  name         required; 1-64 chars; lowercase a-z 0-9 and hyphens only; no leading/
               trailing/consecutive hyphen; not "anthropic"/"claude"; MUST equal the
               parent directory name.
  description  required; 1-1024 chars; non-empty; no angle brackets (no XML tags);
               third person is recommended (warned, not failed).
  top-level    only: name, description, license, allowed-tools, metadata, compatibility.

Usage:
  python3 scripts/validate-skill.py skills/pathfinder skills/map ...
  python3 scripts/validate-skill.py skills/*
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED = {"anthropic", "claude"}
FIRST_PERSON = (" i ", "i can", "i will", "i help", "you can use", "use me ")


def parse_frontmatter(text: str) -> tuple[dict, list[str]]:
    """Minimal YAML-frontmatter parser: top-level scalar keys + nested block keys.

    Returns ({key: value_or_'<block>'}, errors). Values for block keys (e.g.
    metadata:) are recorded as the sentinel "<block>".
    """
    errors: list[str] = []
    if not text.startswith("---"):
        return {}, ["SKILL.md does not start with a YAML frontmatter block (---)"]
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, ["SKILL.md frontmatter is not closed with a second ---"]
    body = parts[1]
    fields: dict[str, str] = {}
    for raw in body.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[0] in (" ", "\t"):
            continue  # nested line under a block key (e.g. metadata:) — block presence is enough
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if not m:
            errors.append(f"unparseable frontmatter line: {raw!r}")
            continue
        key, value = m.group(1), m.group(2).strip()
        # strip matching surrounding quotes
        if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
            value = value[1:-1]
        fields[key] = value if value != "" else "<block>"
    return fields, errors


def validate_skill(skill_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"{skill_dir}: no SKILL.md"], []

    fields, parse_errors = parse_frontmatter(skill_md.read_text())
    errors += [f"{skill_dir.name}: {e}" for e in parse_errors]
    if parse_errors:
        return errors, warnings

    # allowed keys
    for key in fields:
        if key not in ALLOWED_KEYS:
            errors.append(f"{skill_dir.name}: disallowed frontmatter key '{key}' "
                          f"(allowed: {', '.join(sorted(ALLOWED_KEYS))})")

    # name
    name = fields.get("name")
    if not name or name == "<block>":
        errors.append(f"{skill_dir.name}: missing required field 'name'")
    else:
        if len(name) > 64:
            errors.append(f"{skill_dir.name}: name exceeds 64 chars")
        if not NAME_RE.match(name):
            errors.append(f"{skill_dir.name}: name '{name}' must be lowercase a-z/0-9/hyphen, "
                          "no leading/trailing/consecutive hyphen")
        if name in RESERVED:
            errors.append(f"{skill_dir.name}: name must not be a reserved word ({name})")
        if name != skill_dir.name:
            errors.append(f"{skill_dir.name}: name '{name}' must equal the directory name "
                          f"'{skill_dir.name}'")

    # description
    desc = fields.get("description")
    if not desc or desc == "<block>":
        errors.append(f"{skill_dir.name}: missing required field 'description'")
    else:
        if len(desc) > 1024:
            errors.append(f"{skill_dir.name}: description exceeds 1024 chars ({len(desc)})")
        if "<" in desc or ">" in desc:
            errors.append(f"{skill_dir.name}: description must not contain angle brackets (no XML tags)")
        if any(p in f" {desc.lower()} " for p in FIRST_PERSON):
            warnings.append(f"{skill_dir.name}: description may not be third person "
                            "(avoid 'I can…' / 'you can use…')")

    return errors, warnings


def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv] or [p for p in Path("skills").iterdir() if p.is_dir()]
    targets = [t for t in targets if t.is_dir()]
    if not targets:
        print("No skill directories given.", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for t in sorted(targets):
        errs, warns = validate_skill(t)
        all_errors += errs
        all_warnings += warns

    for w in all_warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    if all_errors:
        for e in all_errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"\n✘ {len(all_errors)} frontmatter error(s) across {len(targets)} skill(s).", file=sys.stderr)
        return 1

    print(f"✓ {len(targets)} skill(s) have valid, portable SKILL.md frontmatter.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
