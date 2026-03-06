# Changelog

All notable changes to Pathfinder are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-03-06

### Added
- Monorepo aggregation via `aggregate.py` to merge coverage across modules.
- Visual regression support with `snapshot-compare.py` (pixel-level diff via Pillow, hash fallback).
- `validate-journeys.py` for schema validation of journeys.json files.
- `coverage-score.py` as a standalone script for computing coverage percentage.
- Before/after comparison diagrams with coverage delta tables in `blazes.md`.
- Baseline management flags (`--save-baseline`, `--clear-baseline`) in `generate-diagrams.py`.
- Auto-detection of test directories from framework config files.
- Git hooks (pre-commit, post-commit, pre-push) for journeys.json validation and diagram regeneration.
- CI pipeline with pytest and ruff linting across Python 3.9 and 3.12.
- Claude Code plugin manifest (`.claude-plugin/`) for marketplace distribution.
- SessionStart hook for automatic skill activation.

### Changed
- Installer consolidated into a single `install.sh` with `update`, `uninstall`, and `--version` flags.
- Installation target moved to `~/.agents/` with skills symlinked to `~/.agents/skills/`.
- SKILL.md description shortened for clarity and faster trigger matching.
- `networkidle` references updated from "deprecated" to "unreliable" for accuracy.

### Fixed
- Removed all hardcoded `.pathfinder/` project-level paths in favor of test-directory-scoped artifacts.
- `plugin.json` repository field corrected to a string (was an object).
- Mermaid label escaping for parentheses and double quotes to prevent parse errors.

## [2.0.0] - 2026-02-15

### Added
- Four-phase workflow: `/map`, `/blaze`, `/scout`, `/summit` as separate skills.
- Decision tree diagram combining all journeys into a single flowchart.
- Diamond decision nodes, dashed error arrows, and shared-prefix merging.
- Legend table in every generated `blazes.md`.
- Framework-specific reference docs for Playwright, Cypress, Maestro, Detox, XCUITest, Espresso, and Flutter.
- `generate-ui-test.py` with auto-append to existing test files and auto-create for new ones.
- `detect-ui-framework.py` for automatic framework and platform detection.
- `scan-test-coverage.py` for mapping existing tests to routes and screens.
- Partial coverage status (`"tested": "partial"`) for disabled or implicitly covered steps.
- Color-coded Mermaid nodes: green (tested), amber (partial), red (untested).
- Platform-adaptive terminology (route vs screen, URL change vs push/pop).

### Changed
- `journeys.json` established as the single source of truth for all coverage data.
- Scripts restructured as Python 3 CLIs with JSON stdout and errors to stderr.
- Config moved from project root to `<testDir>/pathfinder/config.json`.

### Fixed
- Duplicate node declarations in decision tree rendering.
- Edge deduplication to prevent repeated arrows in Mermaid output.

## [1.0.0] - 2026-01-20

### Added
- Initial release of Pathfinder.
- Journey discovery from codebase routes, screens, and components.
- Per-journey Mermaid flowcharts with tested/untested markers.
- Coverage summary table with per-journey percentages.
- `pathfinder-init.py` for project initialization with auto-detected framework.
- Support for Playwright and XCUITest test generation.
- `journeys-template.json` starter template.
