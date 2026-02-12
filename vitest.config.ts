import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
    exclude: ['e2e/**', 'node_modules/**'],
    reporters: ['verbose', 'json'],
    outputFile: { json: 'test-results/unit-results.json' },
  },
});
