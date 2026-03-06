# Maestro (React Native / Expo / Flutter / Native Mobile)

## Setup
```bash
curl -Ls "https://get.maestro.mobile.dev" | bash
# iOS: requires simulator
# Android: requires emulator or device
```

## Selectors
```yaml
# Preferred (accessibility)
- tapOn:
    id: "login-button"           # testID / accessibilityLabel
- tapOn: "Submit"                 # visible text
- tapOn:
    text: "Submit"
    index: 0                      # disambiguate duplicates

# Avoid
- tapOn:
    point: "50%,80%"              # brittle coordinates
```

## Waits
```yaml
- waitForAnimationToEnd
- assertVisible: "Welcome"
- extendedWaitUntil:
    visible: "Data loaded"
    timeout: 10000
# NEVER: - swipe ... (as a wait substitute)
```

## Test Pattern
```yaml
# e2e/flows/<CHECKPOINT_ID>.yaml
appId: com.example.app
---
- launchApp

# Arrange
- tapOn: "Tab Name"

# Act
- tapOn:
    id: "action-button"
- inputText: "test input"
- tapOn: "Submit"

# Assert
- assertVisible: "Expected Result"
```

## Screenshots
```yaml
- takeScreenshot: "<checkpoint-id>.png"
```

## Common Commands
| Action | Command |
|--------|---------|
| Run all | `maestro test e2e/flows/` |
| Run one | `maestro test e2e/flows/<CHECKPOINT_ID>.yaml` |
| Record | `maestro record` |
| Studio | `maestro studio` |
