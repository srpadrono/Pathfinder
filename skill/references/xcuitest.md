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
attachment.name = "<checkpoint-id>"
attachment.lifetime = .keepAlways
add(attachment)
```

## Common Commands
| Action | Command |
|--------|---------|
| Run all | `xcodebuild test -scheme App -destination 'platform=iOS Simulator,name=iPhone 16'` |
| Run one | `xcodebuild test -scheme App -only-testing:AppUITests/CHECKPOINT_IDTests` |
