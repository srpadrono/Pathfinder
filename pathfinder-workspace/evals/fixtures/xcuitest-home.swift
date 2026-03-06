import XCTest

final class HomeUITests: XCTestCase {
    let app = XCUIApplication()

    override func setUp() {
        continueAfterFailure = false
        app.launch()
    }

    func testHomeTabLoads() {
        XCTAssertTrue(app.tabBars.buttons["Home"].exists)
        app.tabBars.buttons["Home"].tap()
        XCTAssertTrue(app.navigationBars["Home"].exists)
    }
}
