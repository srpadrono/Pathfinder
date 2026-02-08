# Adding Pathfinder to Your Project

Integrate Pathfinder into an existing repository.

## Quick Start

### 1. Copy Core Files

```bash
# From pathfinder skill directory
cp -r scripts/ your-project/e2e/scripts/
cp -r assets/USER-JOURNEYS-TEMPLATE.md your-project/docs/test-coverage/USER-JOURNEYS.md
cp -r assets/PR_TEMPLATE.md your-project/.github/PULL_REQUEST_TEMPLATE.md
```

### 2. Install Dependencies

```bash
cd your-project
npm install --save-dev playwright @playwright/test dotenv
npx playwright install chromium
```

### 3. Configure Environment

Create `.env.local`:

```bash
TEST_EMAIL=your-test-account@example.com
TEST_PASSWORD=your-test-password
BASE_URL=http://localhost:3000
```

Add to `.gitignore`:

```
.env.local
.auth/
/tmp/test-screenshots/
```

### 4. Add npm Scripts

In `package.json`:

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

After integration:

```
your-project/
├── e2e/
│   ├── scripts/
│   │   ├── setup-auth.ts      # Base camp
│   │   ├── run-tests.ts       # Test runner
│   │   └── update-coverage.ts # Coverage sync
│   ├── test-auth.ts           # Auth journey tests
│   ├── test-dashboard.ts      # Dashboard tests
│   └── test-all.ts            # Run all tests
├── docs/
│   └── test-coverage/
│       └── USER-JOURNEYS.md   # Master trail map
├── .github/
│   ├── workflows/
│   │   └── pathfinder.yml     # CI workflow
│   └── PULL_REQUEST_TEMPLATE.md
├── .auth/
│   └── state.json             # Saved auth (gitignored)
└── .env.local                  # Credentials (gitignored)
```

## Creating Your First Journey

### 1. Add Journey to Trail Map

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

| ID | Checkpoint | Status | Last Run |
|----|------------|--------|----------|
| AUTH-01 | Login success | ❌ | - |
| AUTH-02 | Invalid password | ❌ | - |
```

### 2. Create Test File

Create `e2e/test-auth.ts`:

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
      const url = page.url();
      if (!url.includes('/dashboard')) {
        throw new Error(`Expected dashboard, got ${url}`);
      }
    },
  },
  {
    id: 'AUTH-02',
    journey: 'auth', 
    description: 'Invalid password shows error',
    fn: async (page: Page) => {
      // Clear auth for this test
      await page.context().clearCookies();
      await page.goto(`${BASE}/login`);
      // ... test invalid login
    },
  },
];

// Run if executed directly
if (require.main === module) {
  new TestRunner().run(authTests);
}
```

### 3. Run Tests

```bash
# First time: establish base camp
npm run test:setup

# Run auth tests
npx tsx e2e/test-auth.ts

# Update coverage
npm run test:coverage
```

## Customizing the Runner

### Different Base URL per Environment

```typescript
const BASE_URL = process.env.BASE_URL 
  || process.env.VERCEL_URL 
  || 'http://localhost:3000';
```

### Custom Auth Flow

Modify `setup-auth.ts` for your auth provider:

```typescript
// Auth0, Clerk, Supabase, etc.
if (page.url().includes('clerk.com')) {
  // Handle Clerk login...
} else if (page.url().includes('auth0.com')) {
  // Handle Auth0 login...
}
```

### Adding to Existing Test Suite

If you already have tests, wrap them:

```typescript
import { existingTestFunction } from './legacy-tests';

const CHECKPOINTS = [
  {
    id: 'LEGACY-01',
    description: 'Existing test wrapped',
    fn: async (page) => {
      await existingTestFunction(page);
    },
  },
];
```

## Team Setup

### For Scout (Test Writer)

Focus on:
- `e2e/` directory
- `docs/test-coverage/USER-JOURNEYS.md`
- Flow diagrams and test cases

### For Builder (Implementer)

Focus on:
- `src/` directory
- Making tests pass
- Updating markers in diagrams

### Handoff Convention

In commit messages or PR comments:

```
@builder — Trail marked for AUTH-01, AUTH-02
Tests ready: e2e/test-auth.ts
```

```
@scout — Trail cleared for AUTH-01, AUTH-02
Evidence: /tmp/test-screenshots/2026-02-08/
```
