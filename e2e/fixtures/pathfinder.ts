/**
 * Pathfinder Checkpoint Fixture
 *
 * Custom Playwright fixture that integrates the checkpoint/trail marker system.
 * Use this instead of base `test` to get checkpoint tracking in your tests.
 *
 * Usage:
 *   import { test, expect } from './fixtures/pathfinder';
 *
 *   test('AUTH-01: Login redirects to dashboard', async ({ page, checkpoint }) => {
 *     checkpoint.mark('AUTH-01', 'Login redirects to dashboard');
 *     await page.goto('/dashboard');
 *     await expect(page).toHaveURL(/dashboard/);
 *     checkpoint.clear('AUTH-01');
 *   });
 */

import { test as base, expect } from '@playwright/test';
import * as fs from 'fs';

interface TrailMarker {
  id: string;
  description: string;
  status: 'uncharted' | 'scouted' | 'cleared' | 'unstable' | 'skipped';
  timestamp: string;
}

type PathfinderFixtures = {
  checkpoint: {
    mark: (id: string, description: string) => void;
    clear: (id: string) => void;
    skip: (id: string, reason: string) => void;
    getMarkers: () => TrailMarker[];
  };
};

export const test = base.extend<PathfinderFixtures>({
  checkpoint: async ({}, use, testInfo) => {
    const markers: TrailMarker[] = [];

    await use({
      mark(id: string, description: string) {
        markers.push({
          id,
          description,
          status: 'scouted',
          timestamp: new Date().toISOString(),
        });
        testInfo.annotations.push({
          type: 'checkpoint',
          description: `${id}: ${description}`,
        });
      },

      clear(id: string) {
        const marker = markers.find((m) => m.id === id);
        if (marker) {
          marker.status = 'cleared';
          marker.timestamp = new Date().toISOString();
        }
      },

      skip(id: string, reason: string) {
        const marker = markers.find((m) => m.id === id);
        if (marker) {
          marker.status = 'skipped';
          marker.timestamp = new Date().toISOString();
        }
        testInfo.annotations.push({
          type: 'skip',
          description: `${id}: ${reason}`,
        });
      },

      getMarkers() {
        return [...markers];
      },
    });

    // After test: write markers as JSON for the PathfinderReporter
    if (markers.length > 0) {
      const resultDir = 'test-results';
      fs.mkdirSync(resultDir, { recursive: true });
      const resultFile = `${resultDir}/markers-${testInfo.testId.replace(/[^a-zA-Z0-9]/g, '-')}.json`;
      fs.writeFileSync(resultFile, JSON.stringify(markers, null, 2));
    }
  },
});

export { expect };
