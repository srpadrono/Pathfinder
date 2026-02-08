# Installation

Integrate Pathfinder into an existing project.

## Quick Setup

### 1. Copy Core Files

```bash
# From pathfinder skill directory
cp -r scripts/ your-project/e2e/scripts/
cp assets/USER-JOURNEYS-TEMPLATE.md your-project/docs/test-coverage/USER-JOURNEYS.md
cp assets/PR_TEMPLATE.md your-project/.github/PULL_REQUEST_TEMPLATE.md
```

### 2. Install Dependencies

```bash
npm install --save-dev playwright @playwright/test dotenv
npx playwright install chromium
```

### 3. Environment

Create `.env.local`:
```bash
TEST_EMAIL=test@example.com
TEST_PASSWORD=secret
BASE_URL=http://localhost:3000
```

Add to `.gitignore`:
```
.env.local
.auth/
/tmp/test-screenshots/
```

### 4. npm Scripts

```json
{
  "scripts": {
    "test:setup": "npx tsx e2e/scripts/setup-auth.ts",
    "test:e2e": "npx tsx e2e/test-all.ts",
    "test:coverage": "npx tsx e2e/scripts/update-coverage.ts"
  }
}
```

## Directory Structure

```
project/
├── e2e/
│   ├── scripts/
│   │   ├── setup-auth.ts
│   │   ├── run-tests.ts
│   │   └── update-coverage.ts
│   ├── test-auth.ts
│   └── test-all.ts
├── docs/test-coverage/
│   └── USER-JOURNEYS.md
├── .github/
│   ├── workflows/pathfinder.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── .auth/state.json
└── .env.local
```

## First Journey

### 1. Add to Trail Map

Edit `docs/test-coverage/USER-JOURNEYS.md`:

```markdown
## 🔐 Auth Journey

### Trail Map
\`\`\`mermaid
graph TD
    A[Login Page] --> B{Valid?}
    B -->|Yes| C[Dashboard ❌ AUTH-01]
    B -->|No| D[Error ❌ AUTH-02]
\`\`\`

### Checkpoints
| ID | Checkpoint | Status |
|----|------------|--------|
| AUTH-01 | Login success | ❌ |
| AUTH-02 | Invalid password | ❌ |
```

### 2. Create Test File

`e2e/test-auth.ts`:
```typescript
import { TestRunner, Page, BASE } from './scripts/run-tests';

export const authTests = [
  {
    id: 'AUTH-01',
    journey: 'auth',
    description: 'Login success redirects to dashboard',
    fn: async (page: Page) => {
      await page.goto(`${BASE}/dashboard`);
      await page.waitForSelector('h1');
      if (!page.url().includes('/dashboard')) {
        throw new Error('Expected dashboard');
      }
    },
  },
];

if (require.main === module) {
  new TestRunner().run(authTests);
}
```

### 3. Run

```bash
npm run test:setup   # First time only
npx tsx e2e/test-auth.ts
npm run test:coverage
```

## Team Roles

| Role | Territory | Focus |
|------|-----------|-------|
| Scout | `e2e/`, `USER-JOURNEYS.md` | Tests + diagrams |
| Builder | `src/` | Implementation |

**Handoff:**
```
@builder — Trail marked for AUTH-01, AUTH-02
@scout — Trail cleared for AUTH-01, AUTH-02
```
