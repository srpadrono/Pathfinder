#!/usr/bin/env npx tsx
/**
 * Update Coverage — JSON-based checkpoint state management
 *
 * Reads test results from PathfinderReporter (test-results/checkpoints.json)
 * and updates the structured checkpoint state (checkpoints.json).
 *
 * Usage:
 *   npx tsx scripts/update-coverage.ts
 *   npx tsx scripts/update-coverage.ts --results test-results/checkpoints.json
 *   npx tsx scripts/update-coverage.ts --status WELL-01:pass,WELL-02:fail
 */

import * as fs from 'fs';

interface CheckpointState {
  id: string;
  description: string;
  status: 'pass' | 'fail' | 'skip' | 'wip' | 'uncharted';
  lastRun: string;
  durationMs?: number;
  error?: string;
}

interface JourneyState {
  checkpoints: Record<string, CheckpointState>;
}

interface CoverageState {
  lastUpdated: string;
  journeys: Record<string, JourneyState>;
}

const STATE_FILE = 'checkpoints.json';
const RESULTS_FILE = 'test-results/checkpoints.json';

function loadState(): CoverageState {
  if (fs.existsSync(STATE_FILE)) {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
  }
  return { lastUpdated: new Date().toISOString(), journeys: {} };
}

function saveState(state: CoverageState): void {
  state.lastUpdated = new Date().toISOString();
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function parseArgs(): { resultsFile?: string; manual?: string } {
  const args = process.argv.slice(2);
  let resultsFile: string | undefined;
  let manual: string | undefined;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--results' && args[i + 1]) {
      resultsFile = args[++i];
    } else if (args[i] === '--status' && args[i + 1]) {
      manual = args[++i];
    }
  }

  return { resultsFile, manual };
}

async function main() {
  const { resultsFile, manual } = parseArgs();

  console.log('🗺️  Pathfinder Coverage Update');

  const state = loadState();
  const timestamp = new Date().toISOString().split('T')[0];
  let updateCount = 0;

  if (manual) {
    // Parse manual format: WELL-01:pass,WELL-02:fail
    const entries = manual.split(',').map((item) => {
      const [id, status] = item.split(':');
      return { id: id.trim(), status: status.trim() as CheckpointState['status'] };
    });

    for (const entry of entries) {
      const journeyPrefix = entry.id.replace(/-\d+$/, '').toLowerCase();
      if (!state.journeys[journeyPrefix]) {
        state.journeys[journeyPrefix] = { checkpoints: {} };
      }
      state.journeys[journeyPrefix].checkpoints[entry.id] = {
        id: entry.id,
        description: state.journeys[journeyPrefix].checkpoints[entry.id]?.description || '',
        status: entry.status,
        lastRun: timestamp,
      };
      updateCount++;
    }
    console.log(`   Manual update: ${updateCount} checkpoints`);
  } else {
    // Read from PathfinderReporter output
    const file = resultsFile || RESULTS_FILE;

    if (!fs.existsSync(file)) {
      console.log(`   No results file found at ${file}`);
      console.log('   Run tests first: npx playwright test');
      console.log('   Or use manual: --status WELL-01:pass,WELL-02:fail');
      process.exit(0);
    }

    const data = JSON.parse(fs.readFileSync(file, 'utf-8'));
    const checkpoints = data.checkpoints || {};

    for (const [id, checkpoint] of Object.entries(checkpoints) as [string, any][]) {
      const journeyPrefix = id.replace(/-\d+$/, '').toLowerCase();
      if (!state.journeys[journeyPrefix]) {
        state.journeys[journeyPrefix] = { checkpoints: {} };
      }
      state.journeys[journeyPrefix].checkpoints[id] = {
        id,
        description: checkpoint.description || '',
        status: checkpoint.status,
        lastRun: timestamp,
        durationMs: checkpoint.durationMs,
        error: checkpoint.error,
      };
      updateCount++;
    }
    console.log(`   Read from: ${file}`);
  }

  saveState(state);

  // Print summary
  let totalPassed = 0;
  let totalCheckpoints = 0;

  for (const journey of Object.values(state.journeys)) {
    for (const cp of Object.values(journey.checkpoints)) {
      totalCheckpoints++;
      if (cp.status === 'pass') totalPassed++;
    }
  }

  const coverage = totalCheckpoints > 0 ? Math.round((totalPassed / totalCheckpoints) * 100) : 0;

  console.log(`\n✅ Updated ${updateCount} checkpoints`);
  console.log(`📊 Coverage: ${totalPassed}/${totalCheckpoints} (${coverage}%)`);
  console.log(`📁 State: ${STATE_FILE}`);
  console.log('\nRun `npm run test:generate-map` to regenerate USER-JOURNEYS.md');
}

main().catch((e) => {
  console.error('❌ Update failed:', e.message);
  process.exit(1);
});
