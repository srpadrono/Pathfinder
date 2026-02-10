/**
 * Pathfinder Test Template
 *
 * Copy and adapt for your journeys.
 * Replace JOURNEY and FEAT with your journey/checkpoint names.
 *
 * Run: npx playwright test e2e/<journey>.spec.ts
 * Debug: npx playwright test e2e/<journey>.spec.ts --debug
 */

import { test, expect } from './fixtures/pathfinder';

test.describe('JOURNEY Journey', () => {
  test('FEAT-01: Description of checkpoint', async ({ page, checkpoint }) => {
    checkpoint.mark('FEAT-01', 'Description of checkpoint');

    await page.goto('/feature');
    await expect(page.locator('h1')).toBeVisible();

    checkpoint.clear('FEAT-01');
  });

  test('FEAT-02: Error state displays correctly', async ({ page, checkpoint }) => {
    checkpoint.mark('FEAT-02', 'Error state displays correctly');

    // Mock API error
    await page.route('**/api/data', (route) =>
      route.fulfill({ status: 500, body: 'Server Error' })
    );
    await page.goto('/feature');
    await expect(page.locator('[data-error]')).toBeVisible();

    checkpoint.clear('FEAT-02');
  });

  test('FEAT-03: Empty state shows message', async ({ page, checkpoint }) => {
    checkpoint.mark('FEAT-03', 'Empty state shows message');

    // Mock empty response
    await page.route('**/api/data', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    );
    await page.goto('/feature');
    await expect(page.locator('[data-empty]')).toBeVisible();

    checkpoint.clear('FEAT-03');
  });
});
