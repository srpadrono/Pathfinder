#!/usr/bin/env npx tsx
import * as fs from 'fs';
import * as path from 'path';

type Json = Record<string, unknown>;

function exists(file: string) { return fs.existsSync(file); }
function readJson(file: string): Json { return JSON.parse(fs.readFileSync(file, 'utf-8')); }

const errors: string[] = [];
const warnings: string[] = [];

function assert(cond: boolean, message: string) {
  if (!cond) errors.push(message);
}

function validateState(state: Json) {
  assert(typeof state.version === 'string', 'state.json: `version` must be a string');
  assert(typeof state.currentPhase === 'string', 'state.json: `currentPhase` must be a string');
  const valid = new Set(['survey', 'plan', 'scout', 'build', 'report']);
  if (typeof state.currentPhase === 'string') {
    assert(valid.has(state.currentPhase), `state.json: currentPhase must be one of ${Array.from(valid).join(', ')}`);
  }
}

function validateTask(task: Json, filename: string) {
  assert(typeof task.id === 'string', `${filename}: id must be string`);
  assert(typeof task.description === 'string', `${filename}: description must be string`);
  assert(typeof task.status === 'string', `${filename}: status must be string`);
  if (Array.isArray(task.dependencies)) {
    for (const dep of task.dependencies) {
      assert(typeof dep === 'string', `${filename}: dependency values must be strings`);
    }
  } else {
    errors.push(`${filename}: dependencies must be an array`);
  }
}

function main() {
  const root = '.pathfinder';
  if (!exists(root)) {
    console.log('ℹ️ No .pathfinder directory found (skipping pathfinder schema validation).');
    process.exit(0);
  }

  const statePath = path.join(root, 'state.json');
  if (!exists(statePath)) {
    warnings.push('missing .pathfinder/state.json');
  } else {
    validateState(readJson(statePath));
  }

  const tasksDir = path.join(root, 'tasks');
  if (exists(tasksDir)) {
    const files = fs.readdirSync(tasksDir).filter((f) => f.endsWith('.json'));
    for (const file of files) {
      validateTask(readJson(path.join(tasksDir, file)), `.pathfinder/tasks/${file}`);
    }
  }

  if (warnings.length) {
    console.log('⚠️ Warnings:');
    for (const w of warnings) console.log(`  - ${w}`);
  }

  if (errors.length) {
    console.error('❌ Pathfinder validation failed:');
    for (const e of errors) console.error(`  - ${e}`);
    process.exit(1);
  }

  console.log('✅ Pathfinder files validation passed');
}

main();
