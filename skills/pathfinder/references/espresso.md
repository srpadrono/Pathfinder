# Espresso (Android Native — Kotlin/Java)

## Selectors
```kotlin
// Preferred
onView(withId(R.id.login_button))
onView(withText("Submit"))
onView(withContentDescription("Action button"))

// Avoid
onView(withClassName(endsWith("Button")))
```

## Waits
```kotlin
// Espresso auto-waits via IdlingResource
// For custom async:
IdlingRegistry.getInstance().register(myIdlingResource)

// For RecyclerView
onView(withId(R.id.list))
    .perform(RecyclerViewActions.scrollToPosition<ViewHolder>(5))

// NEVER: Thread.sleep(3000)
```

## Test Pattern
```kotlin
@RunWith(AndroidJUnit4::class)
class CHECKPOINT_IDTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testExpectedBehavior() {
        // Arrange
        onView(withText("Tab")).perform(click())

        // Act
        onView(withId(R.id.action_button)).perform(click())

        // Assert
        onView(withText("Result")).check(matches(isDisplayed()))
    }
}
```

## Screenshots
```kotlin
val screenshot = Screenshot.capture(activityRule.scenario)
screenshot.name = "<checkpoint-id>.png"
screenshot.process()
```

## Common Commands
| Action | Command |
|--------|---------|
| Run all | `./gradlew connectedAndroidTest` |
| Run one | `./gradlew connectedAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=com.app.CHECKPOINT_IDTest` |
