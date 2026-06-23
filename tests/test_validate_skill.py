#!/usr/bin/env python3
"""Tests for scripts/validate-skill.py and the committed skills' frontmatter."""
import importlib.util
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VALIDATOR = os.path.join(REPO, "scripts", "validate-skill.py")

# Import the validator module (filename has a hyphen).
_spec = importlib.util.spec_from_file_location("validate_skill", VALIDATOR)
vs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vs)


def _write_skill(d, name, frontmatter):
    skill_dir = os.path.join(d, name)
    os.makedirs(skill_dir)
    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(f"---\n{frontmatter}\n---\n\n# Body\n")
    return skill_dir


def test_committed_skills_are_compliant():
    """The real shipped skills must pass — this is the CI gate."""
    skills = [os.path.join(REPO, "skills", n)
              for n in ("pathfinder", "map", "blaze", "scout", "summit")]
    r = subprocess.run([sys.executable, VALIDATOR, *skills], capture_output=True, text=True)
    assert r.returncode == 0, f"shipped skills failed frontmatter validation:\n{r.stderr}"


def test_name_must_match_directory():
    with tempfile.TemporaryDirectory() as d:
        from pathlib import Path
        sd = _write_skill(d, "foo", "name: bar\ndescription: A valid description here.")
        errors, _ = vs.validate_skill(Path(sd))
        assert any("must equal the directory name" in e for e in errors)


def test_reserved_name_rejected():
    with tempfile.TemporaryDirectory() as d:
        from pathlib import Path
        sd = _write_skill(d, "claude", "name: claude\ndescription: A valid description here.")
        errors, _ = vs.validate_skill(Path(sd))
        assert any("reserved" in e for e in errors)


def test_angle_brackets_in_description_rejected():
    with tempfile.TemporaryDirectory() as d:
        from pathlib import Path
        sd = _write_skill(d, "foo", "name: foo\ndescription: Uses <xml> tags which are banned.")
        errors, _ = vs.validate_skill(Path(sd))
        assert any("angle brackets" in e for e in errors)


def test_disallowed_key_rejected():
    with tempfile.TemporaryDirectory() as d:
        from pathlib import Path
        sd = _write_skill(d, "foo", "name: foo\ndescription: Fine description.\nbogus: nope")
        errors, _ = vs.validate_skill(Path(sd))
        assert any("disallowed frontmatter key 'bogus'" in e for e in errors)


def test_valid_skill_with_metadata_passes():
    with tempfile.TemporaryDirectory() as d:
        from pathlib import Path
        sd = _write_skill(d, "foo",
                          "name: foo\ndescription: Fine description.\nlicense: MIT\n"
                          "metadata:\n  author: X\n  version: 1.0.0\nallowed-tools: Bash, Read")
        errors, _ = vs.validate_skill(Path(sd))
        assert errors == [], errors


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
