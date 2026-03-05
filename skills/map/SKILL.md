---
name: map
description: "Crawls a codebase to discover all user journeys and creates a journey map (journeys.json) with test coverage status. Use when starting UI test coverage work or when the user says /map."
---

# Mapping

Crawl the codebase to discover every user journey. This is the foundation — nothing gets tested until it's mapped.

## Contents
- [Process](#process)
- [Step status values](#step-status-values)
- [Tips](#tips)
- [Output](#output)

## Process

1. **Detect UI framework:** Run `python3 "${CLAUDE_SKILL_DIR}/../pathfinder/scripts/detect-ui-framework.py" .` to identify the test stack. If `<testDir>/pathfinder/config.json` exists, read the framework from there.

2. **Detect project type** and read entry points:

| Stack | Read these |
|-------|-----------|
| Next.js / React | `app/` or `pages/` routes, layout files, navigation |
| React Native / Expo | `app/` (Expo Router) or navigation config, tab layouts |
| Vue / Nuxt | `pages/`, `router/index.ts` |
| Flutter | `lib/routes/`, `MaterialApp` router, `GoRouter` config |
| SwiftUI (iOS/macOS) | `NavigationStack`, `TabView`, `@Observable` ViewModels, `.sheet`/`.fullScreenCover` modifiers |
| UIKit (iOS) | Storyboards, `UINavigationController`, segues |
| Android (Compose) | `NavHost`, `NavController`, `@Composable` screens |
| Android (XML) | `AndroidManifest.xml`, Navigation graph XML |

3. **For each screen/route**, identify:
   - How the user gets there (navigation path)
   - What actions are available (buttons, forms, gestures)
   - What API calls are made
   - What state changes occur
   - Error states and edge cases
   - **Decision points** — where the user chooses between paths (e.g., Confirm vs Decline)

4. **Group into journeys.** A journey is an end-to-end user goal:
   - Authentication (signup → verify → login → logout)
   - Core CRUD (create → read → update → delete)
   - Feature flows (upload → process → view result)
   - **Error paths** — what happens when API calls fail (separate journey with `id` containing "ERROR")

5. **Check existing test coverage.** For each journey step, search for existing tests:
```bash
python3 "${CLAUDE_SKILL_DIR}/../pathfinder/scripts/scan-test-coverage.py" .
```

6. **Create journey map** (`<testDir>/pathfinder/journeys.json`):
```json
{
  "version": "1.0.0",
  "project": "<name>",
  "framework": "<detected>",
  "journeys": [
    {
      "id": "AUTH",
      "name": "Authentication",
      "steps": [
        { "id": "AUTH-01", "action": "User opens login page", "screen": "LoginView", "tested": false },
        { "id": "AUTH-02", "action": "User enters credentials", "screen": "LoginView", "tested": true, "testFile": "e2e/auth.spec.ts" },
        { "id": "AUTH-03", "action": "User sees dashboard after login", "screen": "DashboardView", "tested": false }
      ]
    },
    {
      "id": "ERROR",
      "name": "Error Handling",
      "steps": [
        { "id": "ERROR-01", "action": "API call fails during login", "screen": "LoginView", "tested": false },
        { "id": "ERROR-02", "action": "Error alert shown with Try Again option", "screen": "LoginView", "tested": false }
      ]
    }
  ]
}
```

7. **Validate the journey map:**
```bash
python3 "${CLAUDE_SKILL_DIR}/../pathfinder/scripts/validate-journeys.py" <testDir>/pathfinder/journeys.json
```

8. **Commit:** `git add <testDir>/pathfinder/journeys.json && git commit -m "Map: Discover N journeys, M steps (X tested, Y pending)"`

### Step status values
| Value | Meaning |
|-------|---------|
| `"tested": true` | Step has a passing UI test |
| `"tested": false` | Step has no test coverage |
| `"tested": "partial"` | Test written but disabled, or implicitly covered |

When marking `"partial"`, add a `"note"` field explaining why (e.g., `"note": "test disabled — needs mock API failure"`).

## Tips

- **Error journeys**: Create a dedicated `ERROR` journey for failure paths. The decision tree generator attaches error branches to loading/API steps automatically by matching `screen` names.
- **Screen names**: Use the actual View/Component name (e.g., `TransactionConfirmationView`) so the decision tree can group steps by screen.
- **Action text**: Write actions as "User does X" — consistent phrasing helps the decision tree merge shared prefixes.
- If routes are dynamic/complex, focus on the main user-facing flows first — skip admin/internal routes.
- If no tests exist at all, mark everything as `tested: false`.

## Output

- `<testDir>/pathfinder/journeys.json` — machine-readable journey map with coverage status
