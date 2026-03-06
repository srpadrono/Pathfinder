# XCUITest (iOS Native — Swift/SwiftUI)

## Selectors
```swift
// Preferred
app.buttons["Submit"]                           // accessibilityIdentifier
app.staticTexts["Welcome"]                      // label
app.textFields["Email"]                         // placeholder

// SwiftUI: set .accessibilityIdentifier("login-btn")
```

## Waits
```swift
let element = app.buttons["Submit"]
XCTAssertTrue(element.waitForExistence(timeout: 5))
// NEVER: sleep(3)
```

## Test Pattern
```swift
class CHECKPOINT_IDTests: XCTestCase {
    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launch()
    }

    func testExpectedBehavior() throws {
        // Arrange
        app.tabBars.buttons["Tab"].tap()

        // Act
        app.buttons["Action"].tap()

        // Assert
        XCTAssertTrue(app.staticTexts["Result"].exists)
    }
}
```

## Screenshots
```swift
let screenshot = app.screenshot()
let attachment = XCTAttachment(screenshot: screenshot)
attachment.name = "<checkpoint-id>.png"
attachment.lifetime = .keepAlways
add(attachment)
```

## SwiftUI Accessibility Identifiers

In SwiftUI views, attach `.accessibilityIdentifier(_:)` to make elements
discoverable by XCUITest. This is the most reliable selector for SwiftUI
because it survives text changes, localization, and view refactors.

```swift
// In your SwiftUI view
Button("Submit") {
    viewModel.submit()
}
.accessibilityIdentifier("submit-button")

TextField("Email", text: $email)
    .accessibilityIdentifier("email-field")

Text(viewModel.errorMessage)
    .accessibilityIdentifier("error-label")
```

### Finding SwiftUI Elements in XCUITest

SwiftUI views do not always map to the element types you expect. Use the
accessibility identifier as the primary lookup, then verify the element type
in the accessibility inspector or with `debugDescription`.

```swift
// Direct lookup by identifier (preferred)
let submitButton = app.buttons["submit-button"]
XCTAssertTrue(submitButton.waitForExistence(timeout: 5))
submitButton.tap()

// Text fields
let emailField = app.textFields["email-field"]
emailField.tap()
emailField.typeText("user@example.com")

// Static text
XCTAssertTrue(app.staticTexts["error-label"].exists)

// When the element type is ambiguous, query all descendants
let element = app.descendants(matching: .any)["submit-button"]
XCTAssertTrue(element.waitForExistence(timeout: 5))
```

### Lists and ScrollViews

SwiftUI `List` and `ScrollView` elements require scrolling before tapping
off-screen items. Use `swipeUp()` or query the cell directly.

```swift
let cell = app.cells["item-row-42"]
while !cell.isHittable {
    app.swipeUp()
}
cell.tap()
```

### iPad and Mac Catalyst Considerations

When testing on iPad or Mac (Designed for iPad), account for these differences:

- **Split views and sidebars**: On iPad, `NavigationSplitView` may show the
  sidebar and detail simultaneously. Tap the sidebar item directly instead of
  relying on back navigation.
- **Popovers vs sheets**: Controls that present a sheet on iPhone may appear
  as a popover on iPad. Query `app.popovers` if `app.sheets` returns no match.
- **Keyboard shortcuts**: Mac Catalyst supports hardware keyboard input. Use
  `app.typeKey("n", modifierFlags: .command)` for keyboard-shortcut testing.
- **Window size**: Set a specific device or window size in the test scheme to
  get consistent layout behavior across runs.

```swift
// iPad: check for popover or sheet
func dismissPresentation() {
    if app.popovers.count > 0 {
        app.popovers.firstMatch.buttons["Done"].tap()
    } else if app.sheets.count > 0 {
        app.sheets.firstMatch.buttons["Done"].tap()
    }
}

// Mac Catalyst: keyboard shortcut
func testKeyboardShortcut() throws {
    app.typeKey("n", modifierFlags: .command)
    XCTAssertTrue(app.textFields["new-item-title"].waitForExistence(timeout: 3))
}
```

## Common Commands
| Action | Command |
|--------|---------|
| Run all | `xcodebuild test -scheme App -destination 'platform=iOS Simulator,name=iPhone 16'` |
| Run one | `xcodebuild test -scheme App -only-testing:AppUITests/CHECKPOINT_IDTests` |
