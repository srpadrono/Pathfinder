/**
 * Pathfinder Checkpoint Fixture
 *
 * Custom Playwright fixture that integrates the checkpoint/trail marker system.
 * Use this instead of base `test` to get checkpoint tracking in your tests.
 */

import { test as base, expect } from '@playwright/test';

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
  },
});

export { expect };
