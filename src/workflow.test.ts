import { describe, expect, it } from 'vitest';
import { isCanonicalPhase, nextPhase } from './workflow';

describe('workflow canonical phases', () => {
  it('validates supported phase names', () => {
    expect(isCanonicalPhase('survey')).toBe(true);
    expect(isCanonicalPhase('plan')).toBe(true);
    expect(isCanonicalPhase('invalid')).toBe(false);
  });

  it('returns the next phase in order', () => {
    expect(nextPhase('survey')).toBe('plan');
    expect(nextPhase('build')).toBe('report');
    expect(nextPhase('report')).toBeNull();
  });
});
