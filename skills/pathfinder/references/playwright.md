# Playwright (Web)

## Setup
```bash
npm init playwright@latest
```

## Selectors
```typescript
// Preferred (accessible)
page.getByRole('button', { name: 'Submit' })
page.getByTestId('login-form')
page.getByLabel('Email')
page.getByPlaceholder('Enter email')
page.getByText('Welcome')

// Avoid
page.locator('.btn-primary')  // brittle CSS
page.locator('#submit')       // implementation detail
```

## Waits
```typescript
await page.waitForLoadState('networkidle')  // unreliable -- prefer condition-based waits below
await expect(page.getByText('Loaded')).toBeVisible()
await page.waitForResponse(resp => resp.url().includes('/api/data'))
// NEVER: await page.waitForTimeout(3000)
```

## Test Pattern
```typescript
import { test, expect } from '@playwright/test'

test('<CHECKPOINT_ID>: <description>', async ({ page }) => {
  // Arrange
  await page.goto('/<route>')

  // Act
  await page.getByRole('button', { name: 'Action' }).click()

  // Assert
  await expect(page.getByText('Result')).toBeVisible()
})
```

## Visual Regression
```typescript
await expect(page).toHaveScreenshot('<checkpoint-id>.png', {
  maxDiffPixelRatio: 0.05,
})
```

## Config (`playwright.config.ts`)
```typescript
export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: true,
  },
})
```

## Common Commands
| Action | Command |
|--------|---------|
| Run all | `npx playwright test` |
| Run one | `npx playwright test -g "<CHECKPOINT_ID>"` |
| Debug | `npx playwright test -g "<CHECKPOINT_ID>" --debug` |
| UI mode | `npx playwright test --ui` |
| Update screenshots | `npx playwright test --update-snapshots` |
| Show report | `npx playwright show-report` |
