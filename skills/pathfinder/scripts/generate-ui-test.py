#!/usr/bin/env python3
"""Generate or append UI tests matching the project's existing patterns.

Usage:
  # New file (no existing test for this journey)
  python3 generate-ui-test.py AUTH-01 "Open login page" playwright --route /login

  # Append to existing journey file
  python3 generate-ui-test.py AUTH-05 "Logout redirects" playwright --route /dashboard --append e2e/tests/auth.spec.ts

  # Auto-detect: appends if journey file exists, creates if not
  python3 generate-ui-test.py AUTH-05 "Logout redirects" playwright --route /dashboard --auto

Options:
  --test-dir     Override test directory (default: auto-detect from config or playwright.config.ts)
  --describe     Group name for test.describe() (default: derived from checkpoint ID prefix)
  --auth         Include authenticated storageState (reads from playwright config)
  --append FILE  Append test to existing file instead of creating new one
  --auto         Auto-detect: append if matching journey file exists, create otherwise
  --output FILE  Output path for new file (default: auto)
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

from pathfinder_paths import find_journeys_file, find_pathfinder_config

# --- Templates ---

PLAYWRIGHT_NEW_FILE = '''import {{ test, expect }} from '@playwright/test'

/**
 * {journey_name} Journey E2E Tests
 */

test.describe('{journey_name}', () => {{
{auth_block}  test('{description}', async ({{ page }}) => {{
    await page.goto('{route}')
{wait_block}
    // Act
    // TODO: implement user actions

    // Assert
    // TODO: add assertions
    await expect(page.getByRole('heading')).toBeVisible()
  }})
}})
'''

PLAYWRIGHT_APPEND = '''
  test('{description}', async ({{ page }}) => {{
    await page.goto('{route}')
{wait_block}
    // Act
    // TODO: implement user actions

    // Assert
    // TODO: add assertions
    await expect(page.getByRole('heading')).toBeVisible()
  }})
'''

CYPRESS_NEW_FILE = '''describe('{journey_name}', () => {{
  {auth_block}it('{description}', () => {{
    cy.visit('{route}')
{wait_block}
    // Act
    // TODO: implement user actions

    // Assert
    // TODO: add assertions
    cy.get('[data-cy="result"]').should('be.visible')
  }})
}})
'''

CYPRESS_APPEND = '''
  it('{description}', () => {{
    cy.visit('{route}')
{wait_block}
    // Act
    // TODO: implement user actions

    // Assert
    cy.get('[data-cy="result"]').should('be.visible')
  }})
'''

MAESTRO_NEW_FILE = '''appId: {app_id}
---
# {journey_name}: {description}

- launchApp

# Arrange
# TODO: navigate to target screen

# Act
# TODO: implement user actions

# Assert
- assertVisible: "TODO"
'''

DETOX_NEW_FILE = '''describe('{journey_name}', () => {{
  beforeAll(async () => {{
    await device.launchApp()
  }})

  it('{description}', async () => {{
    // Arrange
    // TODO: navigate to target screen

    // Act
    // TODO: implement user actions

    // Assert
    await expect(element(by.text('TODO'))).toBeVisible()
  }})
}})
'''

DETOX_APPEND = '''
  it('{description}', async () => {{
    // Arrange
    // TODO: navigate to target screen

    // Act
    // TODO: implement user actions

    // Assert
    await expect(element(by.text('TODO'))).toBeVisible()
  }})
'''

XCUITEST_NEW_FILE = '''import XCTest

class {class_name}Tests: XCTestCase {{
    let app = XCUIApplication()

    override func setUpWithError() throws {{
        continueAfterFailure = false
        app.launch()
    }}

    func test{func_name}() throws {{
        // {description}
        // TODO: implement
        XCTAssertTrue(app.staticTexts["TODO"].exists)
    }}
}}
'''

ESPRESSO_NEW_FILE = '''package com.app.test

import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class {class_name}Test {{
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun test{func_name}() {{
        // {description}
        // TODO: implement
        onView(withText("TODO")).check(matches(isDisplayed()))
    }}
}}
'''

FLUTTER_NEW_FILE = '''import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:app/main.dart' as app;

void main() {{
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('{journey_name}', () {{
    testWidgets('{description}', (tester) async {{
      app.main();
      await tester.pumpAndSettle();

      // Act
      // TODO: implement

      // Assert
      expect(find.text('TODO'), findsOneWidget);
    }});
  }});
}}
'''

FLUTTER_APPEND = '''
    testWidgets('{description}', (tester) async {{
      app.main();
      await tester.pumpAndSettle();

      // Act
      // TODO: implement

      // Assert
      expect(find.text('TODO'), findsOneWidget);
    }});
'''

TEMPLATES_NEW = {
    "playwright": PLAYWRIGHT_NEW_FILE,
    "cypress": CYPRESS_NEW_FILE,
    "maestro": MAESTRO_NEW_FILE,
    "detox": DETOX_NEW_FILE,
    "xcuitest": XCUITEST_NEW_FILE,
    "espresso": ESPRESSO_NEW_FILE,
    "flutter-test": FLUTTER_NEW_FILE,
}

TEMPLATES_APPEND = {
    "playwright": PLAYWRIGHT_APPEND,
    "cypress": CYPRESS_APPEND,
    "detox": DETOX_APPEND,
    "flutter-test": FLUTTER_APPEND,
}

def find_test_dir() -> str:
    """Auto-detect test directory from project config."""
    config_path = find_pathfinder_config()
    if config_path:
        with open(config_path) as f:
            cfg = json.load(f)
            if "testDir" in cfg:
                return cfg["testDir"]
        return os.path.dirname(os.path.dirname(config_path))

    # Check playwright config for testDir
    for cfg_path in [
        "e2e/playwright.config.ts", "playwright.config.ts",
        "e2e/playwright.config.js", "playwright.config.js",
    ]:
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                content = f.read()
            m = re.search(r"testDir:\s*['\"]\.?/?([^'\"]+)['\"]", content)
            if m:
                base = os.path.dirname(cfg_path)
                return os.path.join(base, m.group(1)) if base else m.group(1)
            return os.path.dirname(cfg_path) or "e2e"

    # Check cypress
    for cfg_path in ["cypress.config.ts", "cypress.config.js"]:
        if os.path.exists(cfg_path):
            return "cypress/e2e"

    # Maestro
    if os.path.exists("e2e/.maestro") or os.path.exists("e2e/flows"):
        return "e2e/flows"

    # Flutter
    if os.path.exists("integration_test"):
        return "integration_test"

    return "e2e/tests"


def find_existing_journey_file(journey_prefix: str, test_dir: str, framework: str) -> str | None:
    """Find an existing test file that matches this journey."""
    prefix_lower = journey_prefix.lower().replace("-", "").replace("_", "")

    exts = {"playwright": ".spec.ts", "cypress": ".cy.ts", "detox": ".test.ts",
            "maestro": ".yaml", "flutter-test": "_test.dart",
            "xcuitest": "Tests.swift", "espresso": "Test.kt"}
    ext = exts.get(framework, ".spec.ts")

    matching = (
        glob.glob(os.path.join(test_dir, f"*{ext}"))
        + glob.glob(
            os.path.join(test_dir, "**", f"*{ext}"), recursive=True
        )
    )
    for f in matching:
        basename = os.path.basename(f).lower().replace("-", "").replace("_", "")
        if prefix_lower in basename:
            return f

    return None


def detect_auth_pattern(framework: str) -> str:
    """Detect if the project uses auth setup in tests."""
    if framework != "playwright":
        return ""

    for cfg_path in ["e2e/playwright.config.ts", "playwright.config.ts"]:
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                content = f.read()
            if "storageState" in content:
                return "  // Uses authenticated state from playwright setup project\n\n"
    return ""


def _find_last_describe_closing_brace(lines: list[str]) -> int | None:
    """Find the insertion point before the last describe/group closing brace.

    Uses brace-counting to find the correct closing brace of the last
    top-level describe block. Handles edge cases: multiple describe blocks
    (picks the last one), .only()/.skip() modifiers, and empty describe blocks.
    """
    # Find all top-level describe block start indices
    describe_starts: list[int] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Match describe, test.describe, and variants with .only/.skip
        if re.match(r'(test\.)?describe(\.only|\.skip)?\s*\(', stripped):
            describe_starts.append(i)

    if not describe_starts:
        return None

    # Use the last describe block
    start = describe_starts[-1]

    # Count braces from the start of the last describe block to find its closing
    brace_depth = 0
    found_open = False
    for i in range(start, len(lines)):
        line = lines[i]
        # Strip string literals to avoid counting braces inside strings
        cleaned = re.sub(r'''(['"`])(?:(?!\1).)*\1''', '', line)
        # Strip single-line comments
        cleaned = re.sub(r'//.*$', '', cleaned)
        for ch in cleaned:
            if ch == '{':
                brace_depth += 1
                found_open = True
            elif ch == '}':
                brace_depth -= 1
                if found_open and brace_depth == 0:
                    # This is the closing line of the describe block
                    return i
    return None


def append_to_file(filepath: str, content: str, framework: str) -> str:
    """Append a test to an existing file, inside the last describe/group block."""
    with open(filepath) as f:
        existing = f.read()

    if framework in ("playwright", "cypress", "detox"):
        lines = existing.rstrip().split('\n')

        insert_idx = _find_last_describe_closing_brace(lines)

        if insert_idx is not None:
            lines.insert(insert_idx, content.rstrip())
            result = '\n'.join(lines) + '\n'
        else:
            # Fallback: just append
            result = existing.rstrip() + '\n' + content + '\n'

    elif framework == "flutter-test":
        # Insert before last });
        lines = existing.rstrip().split('\n')

        # Use brace counting for Flutter group blocks too
        insert_idx = None
        brace_depth = 0
        last_group_start = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if re.match(r'group\s*\(', stripped):
                last_group_start = i

        if last_group_start is not None:
            brace_depth = 0
            found_open = False
            for i in range(last_group_start, len(lines)):
                cleaned = re.sub(r'''(['"`])(?:(?!\1).)*\1''', '', lines[i])
                cleaned = re.sub(r'//.*$', '', cleaned)
                for ch in cleaned:
                    if ch == '{':
                        brace_depth += 1
                        found_open = True
                    elif ch == '}':
                        brace_depth -= 1
                        if found_open and brace_depth == 0:
                            insert_idx = i
                            break
                if insert_idx is not None:
                    break

        if insert_idx is None:
            # Fallback: find last });
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == '});':
                    insert_idx = i
                    break

        if insert_idx is not None:
            lines.insert(insert_idx, content.rstrip())
            result = '\n'.join(lines) + '\n'
        else:
            result = existing.rstrip() + '\n' + content + '\n'
    else:
        # Maestro, XCUITest, Espresso — just append
        result = existing.rstrip() + '\n' + content + '\n'

    with open(filepath, 'w') as f:
        f.write(result)

    return filepath


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate or append UI tests")
    parser.add_argument("checkpoint_id", help="e.g. AUTH-01")
    parser.add_argument("description", help="What this test verifies")
    parser.add_argument("framework", choices=list(TEMPLATES_NEW.keys()))
    parser.add_argument("--route", default="/", help="Route/screen to test")
    parser.add_argument("--app-id", default="com.example.app", help="Mobile app ID")
    parser.add_argument("--test-dir", help="Override test directory")
    parser.add_argument("--describe", help="test.describe() group name")
    parser.add_argument("--auth", action="store_true", help="Include auth setup")
    parser.add_argument("--append", help="Append to this existing file")
    parser.add_argument("--auto", action="store_true", help="Auto-detect: append or create")
    parser.add_argument("--output", help="Output path for new file")
    args = parser.parse_args()

    # Check that journeys.json exists when auto-discovering paths
    # Skip the check when explicit --output or --append paths are provided
    if not args.output and not args.append and not args.test_dir:
        journeys_file = find_journeys_file()
        if not journeys_file:
            print("ERROR: journeys.json is missing or not found. "
                  "Run /map first to generate journeys.json before generating tests.", file=sys.stderr)
            print("ERROR: journeys.json is missing or not found. Run /map first.", flush=True)
            sys.exit(1)

    print(f"Using framework: {args.framework}", file=sys.stderr)

    # Derive journey name from checkpoint prefix (AUTH-01 -> AUTH -> Authentication)
    prefix = args.checkpoint_id.rsplit("-", 1)[0] if "-" in args.checkpoint_id else args.checkpoint_id

    # Validate checkpoint ID format
    if not re.match(r'^[A-Za-z]+-\d+$', args.checkpoint_id):
        print(
            f"WARNING: Checkpoint ID '{args.checkpoint_id}' doesn't"
            " match expected PREFIX-NN format (e.g., AUTH-01)",
            file=sys.stderr,
        )

    journey_name = args.describe or prefix.replace("-", " ").replace("_", " ").title()

    test_dir = args.test_dir or find_test_dir()
    _checkpoint_lower = args.checkpoint_id.lower().replace("-", "_")
    class_name = args.checkpoint_id.replace("-", "")
    func_name = args.checkpoint_id.replace("-", "_")

    # Determine: append or new file?
    append_file = args.append
    if not append_file and args.auto:
        append_file = find_existing_journey_file(prefix, test_dir, args.framework)

    # Auth block
    auth_block = detect_auth_pattern(args.framework) if args.auth or args.auto else ""

    # Wait block
    wait_map = {
        "playwright": "    await page.waitForLoadState('domcontentloaded')\n",
        "cypress": "    cy.intercept('GET', '/api/**').as('load')\n    cy.wait('@load')\n",
        "detox": "",
        "maestro": "",
        "flutter-test": "",
        "xcuitest": "",
        "espresso": "",
    }
    wait_block = wait_map.get(args.framework, "")

    template_vars = dict(
        checkpoint_id=args.checkpoint_id,
        description=args.description,
        route=args.route,
        app_id=args.app_id,
        journey_name=journey_name,
        auth_block=auth_block,
        wait_block=wait_block,
        class_name=class_name,
        func_name=func_name,
    )

    if append_file and os.path.exists(append_file):
        # Append mode
        if args.framework not in TEMPLATES_APPEND:
            print(f"ERROR: Append not supported for {args.framework}. Create a new file.", file=sys.stderr)
            sys.exit(1)

        content = TEMPLATES_APPEND[args.framework].format(**template_vars)
        result_path = append_to_file(append_file, content, args.framework)
        print(f"Appended to: {result_path}", file=sys.stderr)
        print(json.dumps({"action": "append", "file": result_path, "checkpoint": args.checkpoint_id}))

    else:
        # New file mode
        content = TEMPLATES_NEW[args.framework].format(**template_vars)

        # Determine output path
        ext_map = {"playwright": ".spec.ts", "cypress": ".cy.ts", "detox": ".test.ts",
                   "maestro": ".yaml", "flutter-test": "_test.dart",
                   "xcuitest": "Tests.swift", "espresso": "Test.kt"}
        ext = ext_map.get(args.framework, ".spec.ts")

        if args.output:
            output = args.output
        else:
            # Use journey prefix as filename (AUTH-01 -> auth.spec.ts)
            filename = prefix.lower().replace(" ", "-").replace("_", "-") + ext
            output = os.path.join(test_dir, filename)

        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, "w") as f:
            f.write(content)
        print(f"Created: {output}", file=sys.stderr)
        print(json.dumps({"action": "create", "file": output, "checkpoint": args.checkpoint_id}))


if __name__ == "__main__":
    main()
