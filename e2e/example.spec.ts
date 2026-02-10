/**
 * Example Pathfinder Test File
 *
 * Demonstrates the checkpoint fixture and Playwright best practices.
 * Copy and adapt for your journeys.
 *
 * Run: npx playwright test e2e/example.spec.ts
 * Debug: npx playwright test e2e/example.spec.ts --debug
 */

import { test, expect } from './fixtures/pathfinder';

test.describe('Example Journey', () => {
  test('EXAMPLE-01: Page loads successfully', async ({ page, checkpoint }) => {
    checkpoint.mark('EXAMPLE-01', 'Page loads successfully');

    await page.goto('/example');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('h1')).toBeVisible();

    checkpoint.clear('EXAMPLE-01');
  });

  test('EXAMPLE-02: User action triggers response', async ({ page, checkpoint }) => {
    checkpoint.mark('EXAMPLE-02', 'User action triggers response');

    await page.goto('/example');
    await page.click('button[data-action="submit"]');
    await expect(page.locator('[data-result]')).toBeVisible();

    checkpoint.clear('EXAMPLE-02');
  });

  test('EXAMPLE-03: Error state displays correctly', async ({ page, checkpoint }) => {
    checkpoint.mark('EXAMPLE-03', 'Error state displays correctly');

    // Mock API error
    await page.route('**/api/data', (route) =>
      route.fulfill({ status: 500, body: 'Server Error' })
    );
    await page.goto('/example');
    await expect(page.locator('[data-error]')).toBeVisible();

    checkpoint.clear('EXAMPLE-03');
  });

  test('EXAMPLE-04: Empty state shows message', async ({ page, checkpoint }) => {
    checkpoint.mark('EXAMPLE-04', 'Empty state shows message');

    // Mock empty response
    await page.route('**/api/data', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    );
    await page.goto('/example');
    await expect(page.locator('[data-empty]')).toBeVisible();

    checkpoint.clear('EXAMPLE-04');
  });
});
