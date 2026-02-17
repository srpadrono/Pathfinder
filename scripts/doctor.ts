#!/usr/bin/env npx tsx
import { existsSync } from 'fs';
import { execSync } from 'child_process';

type Check = { name: string; ok: boolean; details?: string; fix?: string };

function run(cmd: string): { ok: boolean; out: string } {
  try {
    const out = execSync(cmd, { stdio: ['ignore', 'pipe', 'pipe'] }).toString().trim();
    return { ok: true, out };
  } catch (e: any) {
    const out = e?.stdout?.toString?.() || e?.stderr?.toString?.() || String(e);
    return { ok: false, out: out.trim() };
  }
}

const checks: Check[] = [];

checks.push({
  name: 'Node.js >= 18',
  ...(() => {
    const r = run('node -v');
    if (!r.ok) return { ok: false, details: r.out, fix: 'Install Node.js >= 18.' };
    const major = Number((r.out.match(/v(\d+)/) || [])[1] || '0');
    return { ok: major >= 18, details: r.out, fix: 'Upgrade Node.js to >= 18.' };
  })(),
});

checks.push({
  name: 'Playwright browser install',
  ...(() => {
    const r = run('npx playwright --version');
    return { ok: r.ok, details: r.out, fix: 'Run: npx playwright install --with-deps chromium' };
  })(),
});

checks.push({
  name: '.env.local presence',
  ok: existsSync('.env.local'),
  details: existsSync('.env.local') ? 'found' : 'missing',
  fix: 'Create .env.local from documented environment setup.',
});

checks.push({
  name: 'Git hooks path set to .githooks',
  ...(() => {
    const r = run('git config --get core.hooksPath');
    const ok = r.ok && r.out === '.githooks';
    return { ok, details: r.ok ? r.out || '(unset)' : r.out, fix: 'Run: git config core.hooksPath .githooks' };
  })(),
});

checks.push({
  name: 'Canonical workflow spec exists',
  ok: existsSync('docs/architecture/canonical-workflow.md'),
  details: existsSync('docs/architecture/canonical-workflow.md') ? 'found' : 'missing',
  fix: 'Restore docs/architecture/canonical-workflow.md',
});

let fails = 0;
console.log('🩺 Pathfinder doctor\n');
for (const c of checks) {
  const mark = c.ok ? '✅' : '❌';
  console.log(`${mark} ${c.name}${c.details ? ` — ${c.details}` : ''}`);
  if (!c.ok && c.fix) {
    fails += 1;
    console.log(`   Fix: ${c.fix}`);
  }
}

if (fails > 0) {
  console.log(`\n❌ Doctor found ${fails} issue(s).`);
  process.exit(1);
}

console.log('\n✅ Environment looks healthy.');
