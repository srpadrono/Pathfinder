import { defineConfig, devices } from '@playwright/test';
import dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['./e2e/reporters/pathfinder-reporter.ts'],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    screenshot: 'on',
    trace: 'on-first-retry',
    video: 'on-first-retry',
  },
  projects: [
    // Auth setup runs first
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    // All journeys depend on auth
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: '.auth/state.json' },
      dependencies: ['setup'],
    },
  ],
});
