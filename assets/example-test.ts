/**
 * Example Pathfinder Test File
 * 
 * Copy and adapt for your journeys.
 * Each checkpoint represents a point on the trail that must be cleared.
 */

import { TestRunner, Page, BASE } from '../scripts/run-tests';

// Define all checkpoints for this journey
export const exampleCheckpoints = [
  {
    id: 'EXAMPLE-01',
    journey: 'example',
    description: 'Page loads successfully',
    fn: async (page: Page) => {
      await page.goto(`${BASE}/example`);
      await page.waitForLoadState('networkidle');
      
      // Verify page loaded
      const header = page.locator('h1');
      if (!(await header.isVisible({ timeout: 5000 }))) {
        throw new Error('Page header not found — checkpoint blocked');
      }
    },
  },
  
  {
    id: 'EXAMPLE-02',
    journey: 'example',
    description: 'User action triggers response',
    fn: async (page: Page) => {
      // Perform action
      await page.click('button[data-action="submit"]');
      
      // Verify response
      const result = page.locator('[data-result]');
      if (!(await result.isVisible({ timeout: 5000 }))) {
        throw new Error('Action result not visible — checkpoint blocked');
      }
    },
  },
  
  {
    id: 'EXAMPLE-03',
    journey: 'example',
    description: 'Error state displays correctly',
    fn: async (page: Page) => {
      // Trigger error condition
      await page.route('**/api/data', route => 
        route.fulfill({ status: 500, body: 'Server Error' })
      );
      await page.reload();
      
      // Verify error message
      const error = page.locator('[data-error]');
      if (!(await error.isVisible({ timeout: 5000 }))) {
        throw new Error('Error message not displayed — hazard not handled');
      }
    },
  },
  
  {
    id: 'EXAMPLE-04',
    journey: 'example',
    description: 'Empty state shows message',
    fn: async (page: Page) => {
      // Mock empty response
      await page.route('**/api/data', route =>
        route.fulfill({ status: 200, json: [] })
      );
      await page.reload();
      
      // Verify empty state
      const empty = page.locator('[data-empty]');
      if (!(await empty.isVisible({ timeout: 5000 }))) {
        throw new Error('Empty state not shown — clearing not marked');
      }
    },
  },
];

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const runner = new TestRunner();
  runner.run(exampleCheckpoints);
}
