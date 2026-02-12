import { describe, expect, it } from 'vitest';
import { mkdtempSync, mkdirSync, copyFileSync, writeFileSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';
import { spawnSync } from 'child_process';

function run(cmd: string, args: string[], cwd: string) {
  return spawnSync(cmd, args, { cwd, encoding: 'utf-8' });
}

describe('verify-expedition preflight', () => {
  it('returns actionable exit code when .pathfinder/state.json is missing', () => {
    const dir = mkdtempSync(join(tmpdir(), 'pathfinder-verify-'));
    mkdirSync(join(dir, 'scripts'));
    copyFileSync('scripts/verify-expedition.sh', join(dir, 'scripts/verify-expedition.sh'));

    const runResult = run('bash', ['scripts/verify-expedition.sh'], dir);

    expect(runResult.status).toBe(2);
    expect(runResult.stdout).toContain('Missing .pathfinder/state.json');
    expect(runResult.stdout).toContain('To initialize, create:');
  });

  it('detects custom default branch names (trunk) before gate checks', () => {
    const dir = mkdtempSync(join(tmpdir(), 'pathfinder-verify-'));
    mkdirSync(join(dir, 'scripts'));
    mkdirSync(join(dir, '.pathfinder'));
    copyFileSync('scripts/verify-expedition.sh', join(dir, 'scripts/verify-expedition.sh'));

    run('git', ['init', '-b', 'trunk'], dir);
    run('git', ['config', 'user.email', 'test@example.com'], dir);
    run('git', ['config', 'user.name', 'tester'], dir);
    writeFileSync(join(dir, 'README.md'), 'x');
    run('git', ['add', '.'], dir);
    run('git', ['commit', '-m', 'init'], dir);

    writeFileSync(
      join(dir, '.pathfinder/state.json'),
      JSON.stringify({ expedition: 'demo', branch: 'feat/test', currentPhase: 'report' }, null, 2)
    );

    const runResult = run('bash', ['scripts/verify-expedition.sh'], dir);

    expect(runResult.stdout).toContain('Base branch: trunk');
    expect(runResult.status).toBe(1); // missing gate files
  });
});
