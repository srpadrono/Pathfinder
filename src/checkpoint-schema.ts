export type CheckpointStatus = 'pass' | 'fail' | 'skip';

export interface CheckpointRecord {
  id: string;
  description: string;
  status: CheckpointStatus;
  durationMs: number;
  error?: string;
  journey?: string;
}

export interface CheckpointsPayload {
  timestamp: string;
  durationMs: number;
  status: string;
  summary: {
    passed: number;
    failed: number;
    skipped: number;
    total: number;
    coverage: number;
  };
  checkpoints: Record<string, CheckpointRecord>;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

export function validateCheckpointsPayload(data: unknown): string[] {
  const errors: string[] = [];
  if (!isObject(data)) {
    return ['payload must be a JSON object'];
  }

  if (typeof data.timestamp !== 'string') errors.push('timestamp must be string');
  if (typeof data.durationMs !== 'number') errors.push('durationMs must be number');
  if (!isObject(data.summary)) {
    errors.push('summary must be object');
  } else {
    for (const key of ['passed', 'failed', 'skipped', 'total', 'coverage'] as const) {
      if (typeof data.summary[key] !== 'number') errors.push(`summary.${key} must be number`);
    }
  }

  if (!isObject(data.checkpoints)) {
    errors.push('checkpoints must be object');
  } else {
    for (const [id, cp] of Object.entries(data.checkpoints)) {
      if (!isObject(cp)) {
        errors.push(`checkpoints.${id} must be object`);
        continue;
      }
      if (typeof cp.id !== 'string') errors.push(`checkpoints.${id}.id must be string`);
      if (typeof cp.description !== 'string') errors.push(`checkpoints.${id}.description must be string`);
      if (!['pass', 'fail', 'skip'].includes(String(cp.status))) {
        errors.push(`checkpoints.${id}.status must be pass|fail|skip`);
      }
      if (typeof cp.durationMs !== 'number') errors.push(`checkpoints.${id}.durationMs must be number`);
    }
  }

  return errors;
}
