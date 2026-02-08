# CI/CD Integration

Run Pathfinder tests in continuous integration pipelines.

## GitHub Actions

### Basic Workflow

```yaml
# .github/workflows/pathfinder.yml
name: Pathfinder Tests

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  scout:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright
        run: npx playwright install --with-deps chromium
      
      - name: Run tests
        env:
          TEST_EMAIL: ${{ secrets.TEST_EMAIL }}
          TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
          BASE_URL: http://localhost:3000
        run: |
          npm run dev &
          sleep 10
          npx tsx e2e/test-all.ts
      
      - name: Upload evidence
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-screenshots
          path: /tmp/test-screenshots/
          retention-days: 7
      
      - name: Update coverage
        if: success()
        run: npx tsx scripts/update-coverage.ts
```

### With Coverage Comment

```yaml
      - name: Comment coverage on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const coverage = fs.readFileSync('docs/test-coverage/USER-JOURNEYS.md', 'utf8');
            const match = coverage.match(/Total Coverage:\s*(\d+)%/);
            const percent = match ? match[1] : '?';
            
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## 🗺️ Pathfinder Report\n\n**Coverage:** ${percent}%\n\nSee [evidence](../actions/runs/${context.runId}) for screenshots.`
            });
```

## Environment Secrets

Required secrets in GitHub repository settings:

| Secret | Description |
|--------|-------------|
| `TEST_EMAIL` | Test account email |
| `TEST_PASSWORD` | Test account password |

**Never commit credentials.** Always use secrets.

## Test Runner Script

Create `e2e/test-all.ts` to run all journeys:

```typescript
#!/usr/bin/env npx tsx
import { TestRunner } from '../scripts/run-tests';
import { authTests } from './test-auth';
import { dashboardTests } from './test-dashboard';
import { wellsTests } from './test-wells';

const ALL_TESTS = [
  ...authTests,
  ...dashboardTests,
  ...wellsTests,
];

const runner = new TestRunner();
runner.run(ALL_TESTS).then(results => {
  // Write results for coverage update
  const fs = require('fs');
  fs.writeFileSync('/tmp/test-results.json', JSON.stringify(results));
  
  // Exit with failure if any tests failed
  const failed = results.filter(r => r.status === 'fail').length;
  process.exit(failed > 0 ? 1 : 0);
});
```

## Headless Mode

For CI, run Playwright in headless mode:

```typescript
// scripts/run-tests.ts
const isCI = process.env.CI === 'true';

const browser = await chromium.launch({ 
  headless: isCI,  // Headless in CI, visible locally
});
```

## Matrix Testing

Test across multiple browsers:

```yaml
jobs:
  test:
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
    
    steps:
      - name: Install Playwright
        run: npx playwright install --with-deps ${{ matrix.browser }}
      
      - name: Run tests
        run: BROWSER=${{ matrix.browser }} npx tsx e2e/test-all.ts
```

## Scheduled Expeditions

Run tests on a schedule:

```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  
jobs:
  nightly-scout:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # ... same as above
      
      - name: Notify on failure
        if: failure()
        run: |
          curl -X POST "${{ secrets.SLACK_WEBHOOK }}" \
            -H 'Content-Type: application/json' \
            -d '{"text":"🚨 Nightly Pathfinder expedition failed!"}'
```

## Badge

Add coverage badge to README:

```markdown
![Coverage](https://img.shields.io/badge/coverage-85%25-green)
```

Or use dynamic badge with coverage parsing in CI.
