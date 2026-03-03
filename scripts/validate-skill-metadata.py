#!/usr/bin/env python3
"""Validate skill metadata (name + description) against agentskills.io spec."""
import re
import sys
import argparse


def validate_metadata(name, description):
    errors = []

    if not (1 <= len(name) <= 64):
        errors.append(f"NAME ERROR: '{name}' is {len(name)} characters. Must be 1-64.")

    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        errors.append(f"NAME ERROR: '{name}' has invalid characters. Use lowercase, numbers, single hyphens.")

    if len(description) > 1024:
        errors.append(f"DESCRIPTION ERROR: {len(description)} chars. Must be ≤1024.")

    first_person = {"i", "me", "my", "we", "our", "you", "your"}
    found = first_person.intersection(set(re.findall(r'\b\w+\b', description.lower())))
    if found:
        errors.append(f"STYLE WARNING: First/second person terms found: {found}. Use third-person imperative.")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    else:
        print(f"SUCCESS: '{name}' metadata is valid.")
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    args = parser.parse_args()
    validate_metadata(args.name, args.description)
