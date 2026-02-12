import { describe, expect, it } from 'vitest';
import { mkdtempSync, mkdirSync, copyFileSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';
import { spawnSync } from 'child_process';

describe('verify-expedition preflight', () => {
  it('returns actionable exit code when .pathfinder/state.json is missing', () => {
    const dir = mkdtempSync(join(tmpdir(), 'pathfinder-verify-'));
    mkdirSync(join(dir, 'scripts'));
    copyFileSync('scripts/verify-expedition.sh', join(dir, 'scripts/verify-expedition.sh'));

    const run = spawnSync('bash', ['scripts/verify-expedition.sh'], {
      cwd: dir,
      encoding: 'utf-8',
    });

    expect(run.status).toBe(2);
    expect(run.stdout).toContain('Missing .pathfinder/state.json');
    expect(run.stdout).toContain('To initialize, create:');
  });
});
