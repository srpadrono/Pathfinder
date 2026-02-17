export const CANONICAL_PHASES = ['survey', 'plan', 'scout', 'build', 'report'] as const;

export type Phase = (typeof CANONICAL_PHASES)[number];

export function isCanonicalPhase(value: string): value is Phase {
  return (CANONICAL_PHASES as readonly string[]).includes(value);
}

export function nextPhase(phase: Phase): Phase | null {
  const idx = CANONICAL_PHASES.indexOf(phase);
  return idx >= 0 && idx < CANONICAL_PHASES.length - 1 ? CANONICAL_PHASES[idx + 1] : null;
}
