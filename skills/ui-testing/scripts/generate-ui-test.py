#!/usr/bin/env python3
"""Generate a UI test skeleton for a checkpoint.

Usage: python3 generate-ui-test.py <checkpoint-id> <description> <framework> [--route /path] [--output path/to/test]

Outputs the test file content to stdout if no --output, or writes to file.
"""
import argparse, sys, os, json

TEMPLATES = {
    "playwright": '''import {{ test, expect }} from '@playwright/test'

test('{checkpoint_id}: {description}', async ({{ page }}) => {{
  // Arrange
  await page.goto('{route}')

  // Act
  // TODO: implement user actions

  // Assert
  // TODO: add assertions
  await expect(page.getByText('TODO')).toBeVisible()
}})
''',
    "cypress": '''describe('{checkpoint_id}: {description}', () => {{
  it('should {description_lower}', () => {{
    // Arrange
    cy.visit('{route}')

    // Act
    // TODO: implement user actions

    // Assert
    // TODO: add assertions
    cy.contains('TODO').should('be.visible')
  }})
}})
''',
    "maestro": '''appId: {app_id}
---
# {checkpoint_id}: {description}

- launchApp

# Arrange
# TODO: navigate to target screen

# Act
# TODO: implement user actions

# Assert
- assertVisible: "TODO"
''',
    "detox": '''describe('{checkpoint_id}: {description}', () => {{
  beforeAll(async () => {{
    await device.launchApp()
  }})

  it('should {description_lower}', async () => {{
    // Arrange
    // TODO: navigate to target screen

    // Act
    // TODO: implement user actions

    // Assert
    await expect(element(by.text('TODO'))).toBeVisible()
  }})
}})
''',
    "xcuitest": '''import XCTest

class {checkpoint_class}Tests: XCTestCase {{
    let app = XCUIApplication()

    override func setUpWithError() throws {{
        continueAfterFailure = false
        app.launch()
    }}

    func test{checkpoint_func}() throws {{
        // {description}

        // Arrange
        // TODO: navigate to target screen

        // Act
        // TODO: implement user actions

        // Assert
        XCTAssertTrue(app.staticTexts["TODO"].exists)
    }}
}}
''',
    "espresso": '''package com.app.test

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
class {checkpoint_class}Test {{
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun test{checkpoint_func}() {{
        // {description}

        // Arrange
        // TODO: navigate to target screen

        // Act
        // TODO: implement user actions

        // Assert
        onView(withText("TODO")).check(matches(isDisplayed()))
    }}
}}
''',
    "flutter-test": '''import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:app/main.dart' as app;

void main() {{
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('{checkpoint_id}: {description}', (tester) async {{
    // Arrange
    app.main();
    await tester.pumpAndSettle();

    // Act
    // TODO: implement user actions

    // Assert
    expect(find.text('TODO'), findsOneWidget);
  }});
}}
''',
}

# Default output paths per framework
DEFAULT_PATHS = {
    "playwright": "e2e/{checkpoint_lower}.spec.ts",
    "cypress": "cypress/e2e/{checkpoint_lower}.cy.ts",
    "maestro": "e2e/flows/{checkpoint_lower}.yaml",
    "detox": "e2e/{checkpoint_lower}.test.ts",
    "xcuitest": "AppUITests/{checkpoint_class}Tests.swift",
    "espresso": "app/src/androidTest/java/com/app/test/{checkpoint_class}Test.kt",
    "flutter-test": "integration_test/{checkpoint_lower}_test.dart",
}

def main():
    parser = argparse.ArgumentParser(description="Generate UI test skeleton")
    parser.add_argument("checkpoint_id", help="e.g. FEAT-01")
    parser.add_argument("description", help="What this test verifies")
    parser.add_argument("framework", choices=list(TEMPLATES.keys()))
    parser.add_argument("--route", default="/", help="Route/screen to test")
    parser.add_argument("--app-id", default="com.example.app", help="Mobile app ID")
    parser.add_argument("--output", help="Output file path (default: auto)")
    args = parser.parse_args()

    # Build template vars
    checkpoint_lower = args.checkpoint_id.lower().replace("-", "_")
    checkpoint_class = args.checkpoint_id.replace("-", "")
    checkpoint_func = args.checkpoint_id.replace("-", "_")

    content = TEMPLATES[args.framework].format(
        checkpoint_id=args.checkpoint_id,
        description=args.description,
        description_lower=args.description[0].lower() + args.description[1:] if args.description else "",
        route=args.route,
        app_id=args.app_id,
        checkpoint_lower=checkpoint_lower,
        checkpoint_class=checkpoint_class,
        checkpoint_func=checkpoint_func,
    )

    output = args.output or DEFAULT_PATHS[args.framework].format(
        checkpoint_lower=checkpoint_lower,
        checkpoint_class=checkpoint_class,
    )

    if args.output or not sys.stdout.isatty():
        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, "w") as f:
            f.write(content)
        print(f"Generated: {output}", file=sys.stderr)
    else:
        print(f"# Output path: {output}")
        print(content)

if __name__ == "__main__":
    main()
