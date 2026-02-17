import { describe, expect, it } from 'vitest';
import { validateCheckpointsPayload } from './checkpoint-schema';

describe('validateCheckpointsPayload', () => {
  it('accepts valid payload', () => {
    const data = {
      timestamp: new Date().toISOString(),
      durationMs: 100,
      status: 'passed',
      summary: { passed: 1, failed: 0, skipped: 0, total: 1, coverage: 100 },
      checkpoints: {
        'EXAMPLE-01': {
          id: 'EXAMPLE-01',
          description: 'ok',
          status: 'pass',
          durationMs: 10,
        },
      },
    };
    expect(validateCheckpointsPayload(data)).toEqual([]);
  });

  it('reports structural errors', () => {
    const errors = validateCheckpointsPayload({ timestamp: 1, checkpoints: [] });
    expect(errors.length).toBeGreaterThan(0);
    expect(errors.some((e) => e.includes('timestamp must be string'))).toBe(true);
  });
});
