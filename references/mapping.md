# Mapping

Crawl the codebase to discover every user journey. This is the foundation — nothing gets tested until it's mapped.

## Process

1. **Detect UI framework:** Run `python3 scripts/detect-ui-framework.py .` to identify the test stack. If `.pathfinder/config.json` exists, read the framework from there.

2. **Detect project type** and read entry points:

| Stack | Read these |
|-------|-----------|
| Next.js / React | `app/` or `pages/` routes, layout files, navigation |
| React Native / Expo | `app/` (Expo Router) or navigation config, tab layouts |
| Vue / Nuxt | `pages/`, `router/index.ts` |
| Flutter | `lib/routes/`, `MaterialApp` router |
| iOS | Storyboards, `NavigationStack`, `TabView` |
| Android | `AndroidManifest.xml`, Navigation graph |

3. **For each screen/route**, identify:
   - How the user gets there (navigation path)
   - What actions are available (buttons, forms, gestures)
   - What API calls are made
   - What state changes occur
   - Error states and edge cases

4. **Group into journeys.** A journey is an end-to-end user goal:
   - Authentication (signup → verify → login → logout)
   - Core CRUD (create → read → update → delete)
   - Feature flows (upload → process → view result)

5. **Check existing test coverage.** For each journey step, search for existing tests:
```bash
python3 scripts/scan-test-coverage.py .
```

6. **Create journey map** (`.pathfinder/journeys.json`):
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
        { "id": "AUTH-01", "action": "User opens login page", "screen": "/login", "tested": false },
        { "id": "AUTH-02", "action": "User enters credentials", "screen": "/login", "tested": true, "testFile": "e2e/auth.spec.ts" },
        { "id": "AUTH-03", "action": "User sees dashboard after login", "screen": "/dashboard", "tested": false }
      ]
    }
  ]
}
```

7. **Commit:** `git add .pathfinder/journeys.json && git commit -m "Map: Discover N journeys, M steps (X tested, Y pending)"`

## Error Handling

- If routes are dynamic/complex, focus on the main user-facing flows first — skip admin/internal routes.
- If no tests exist at all, mark everything as `tested: false`.
- If test files exist but you can't determine which journey they cover, mark as `tested: "partial"`.

## Output

- `.pathfinder/journeys.json` — machine-readable journey map with coverage status
