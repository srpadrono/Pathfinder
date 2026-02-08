# CI/CD Integration

Run Pathfinder tests in GitHub Actions.

## Basic Workflow

```yaml
# .github/workflows/pathfinder.yml
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
      
      - name: Run tests
        env:
          TEST_EMAIL: ${{ secrets.TEST_EMAIL }}
          TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
          BASE_URL: http://localhost:3000
        run: |
          npm run dev &
          sleep 10
          npx tsx e2e/test-all.ts
      
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: screenshots
          path: /tmp/test-screenshots/
          retention-days: 7
```

## Required Secrets

| Secret | Description |
|--------|-------------|
| `TEST_EMAIL` | Test account email |
| `TEST_PASSWORD` | Test account password |

## Test Runner

`e2e/test-all.ts`:
```typescript
import { TestRunner } from '../scripts/run-tests';
import { authTests } from './test-auth';
import { dashboardTests } from './test-dashboard';

const ALL = [...authTests, ...dashboardTests];

new TestRunner().run(ALL).then(results => {
  require('fs').writeFileSync('/tmp/test-results.json', JSON.stringify(results));
  const failed = results.filter(r => r.status === 'fail').length;
  process.exit(failed > 0 ? 1 : 0);
});
```

## Headless Mode

```typescript
// run-tests.ts
const browser = await chromium.launch({ 
  headless: process.env.CI === 'true'
});
```

## Coverage Comment

```yaml
- uses: actions/github-script@v7
  if: github.event_name == 'pull_request'
  with:
    script: |
      const fs = require('fs');
      const coverage = fs.readFileSync('docs/test-coverage/USER-JOURNEYS.md', 'utf8');
      const match = coverage.match(/Coverage:\s*(\d+)%/);
      github.rest.issues.createComment({
        ...context.repo,
        issue_number: context.issue.number,
        body: `## 🗺️ Coverage: ${match?.[1] || '?'}%`
      });
```

## Scheduled Runs

```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Daily 6 AM UTC
```

## Matrix Testing

```yaml
strategy:
  matrix:
    browser: [chromium, firefox, webkit]
steps:
  - run: npx playwright install --with-deps ${{ matrix.browser }}
  - run: BROWSER=${{ matrix.browser }} npx tsx e2e/test-all.ts
```
