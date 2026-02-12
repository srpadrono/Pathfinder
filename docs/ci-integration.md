# CI/CD Integration

Run Pathfinder tests in GitHub Actions.

## Workflow

The project includes `.github/workflows/pathfinder.yml`. Key steps:

```yaml
name: Pathfinder
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci
      - run: npx playwright install --with-deps chromium

      - name: Run E2E tests
        run: npx playwright test
        env:
          CI: true
          BASE_URL: http://localhost:3000
          TEST_EMAIL: ${{ secrets.TEST_EMAIL }}
          TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}

      - name: Run unit tests
        run: npx vitest run

      - name: Update coverage
        if: always()
        run: npx tsx scripts/update-coverage.ts

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 14

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: test-results/
          retention-days: 7
```

## How It Works

- **Dev server**: Playwright's `webServer` config in `playwright.config.ts` starts the server automatically — no manual `npm run dev & sleep 10`
- **Temp paths**: Use `test-results/` (relative, cross-platform) not `/tmp/`
- **Coverage data**: Read from `test-results/checkpoints.json` (produced by PathfinderReporter)

## Required Secrets

| Secret | Description |
|--------|-------------|
| `TEST_EMAIL` | Test account email |
| `TEST_PASSWORD` | Test account password |

## CI-Specific Config

`playwright.config.ts` detects CI automatically:

```typescript
forbidOnly: !!process.env.CI,    // Block .only() in CI
retries: process.env.CI ? 2 : 0, // Retry flakes
workers: process.env.CI ? 1 : undefined,
```

## PR Coverage Comment

```yaml
- uses: actions/github-script@v7
  if: github.event_name == 'pull_request'
  with:
    script: |
      const fs = require('fs');
      const data = JSON.parse(fs.readFileSync('test-results/checkpoints.json', 'utf8'));
      const { passed, total, coverage } = data.summary;
      github.rest.issues.createComment({
        ...context.repo,
        issue_number: context.issue.number,
        body: `## 🗺️ Pathfinder Coverage: ${coverage}%\n\n✅ Cleared: ${passed} | 📊 Total: ${total}`
      });
```

## Scheduled & Matrix Testing

```yaml
# Daily smoke test
on:
  schedule:
    - cron: '0 6 * * *'

# Multi-browser
strategy:
  matrix:
    browser: [chromium, firefox, webkit]
steps:
  - run: npx playwright install --with-deps ${{ matrix.browser }}
  - run: npx playwright test --project=${{ matrix.browser }}
```
