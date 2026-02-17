#!/usr/bin/env npx tsx
import * as fs from 'fs';

const files = {
  agents: 'AGENTS.md',
  readme: 'README.md',
  meta: 'skills/using-pathfinder/SKILL.md',
  canonical: 'docs/architecture/canonical-workflow.md',
};

const canonicalSkills = [
  'pathfinder:surveying',
  'pathfinder:planning',
  'pathfinder:scouting',
  'pathfinder:unit-testing',
  'pathfinder:building',
  'pathfinder:reporting',
  'pathfinder:dispatching',
  'pathfinder:git-workflow',
  'pathfinder:code-review',
  'pathfinder:security',
  'pathfinder:systematic-debugging',
];

const deprecatedSkills = [
  'pathfinder:charting',
  'pathfinder:marking',
  'pathfinder:test-driven-development',
  'pathfinder:verification-before-completion',
];

function read(path: string): string {
  if (!fs.existsSync(path)) throw new Error(`Missing required file: ${path}`);
  return fs.readFileSync(path, 'utf-8');
}

function ensureIncludes(content: string, values: string[], file: string): string[] {
  return values.filter((value) => !content.includes(value)).map((value) => `${file} missing \`${value}\``);
}

function ensureExcludes(content: string, values: string[], file: string): string[] {
  return values.filter((value) => content.includes(value)).map((value) => `${file} contains deprecated \`${value}\``);
}

function main() {
  const agents = read(files.agents);
  const readme = read(files.readme);
  const meta = read(files.meta);
  const canonical = read(files.canonical);

  const errors: string[] = [];

  // Canonical file must list all canonical skills.
  errors.push(...ensureIncludes(canonical, canonicalSkills, files.canonical));

  // AGENTS + meta-skill must use canonical skills and avoid deprecated ones.
  errors.push(...ensureIncludes(agents, ['pathfinder:planning', 'pathfinder:unit-testing'], files.agents));
  errors.push(...ensureExcludes(agents, deprecatedSkills, files.agents));

  errors.push(...ensureIncludes(meta, ['pathfinder:planning', 'pathfinder:unit-testing'], files.meta));
  errors.push(...ensureExcludes(meta, deprecatedSkills, files.meta));

  // README must reference canonical workflow doc.
  errors.push(...ensureIncludes(readme, ['docs/architecture/canonical-workflow.md'], files.readme));

  if (errors.length > 0) {
    console.error('❌ Documentation validation failed:');
    for (const err of errors) console.error(`  - ${err}`);
    process.exit(1);
  }

  console.log('✅ Documentation validation passed');
}

main();
