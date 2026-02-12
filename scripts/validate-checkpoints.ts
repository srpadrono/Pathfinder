#!/usr/bin/env npx tsx
import * as fs from 'fs';
import { validateCheckpointsPayload } from '../src/checkpoint-schema';

const file = process.argv[2] || 'test-results/checkpoints.json';

if (!fs.existsSync(file)) {
  console.log(`ℹ️ No checkpoint report found at ${file} (skip).`);
  process.exit(0);
}

const raw = JSON.parse(fs.readFileSync(file, 'utf-8'));
const errors = validateCheckpointsPayload(raw);

if (errors.length > 0) {
  console.error(`❌ Invalid checkpoint report schema in ${file}:`);
  for (const err of errors) console.error(`  - ${err}`);
  process.exit(1);
}

console.log(`✅ Checkpoint report schema valid (${file})`);
