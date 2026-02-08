#!/usr/bin/env npx tsx
/**
 * Update Coverage - Syncs test results to USER-JOURNEYS.md
 * 
 * Reads test results JSON and updates the trail map with current status.
 * 
 * Usage: npx tsx update-coverage.ts --results /tmp/test-results.json
 *        npx tsx update-coverage.ts --journey wells --status WELL-01:pass,WELL-02:fail
 */

import * as fs from 'fs';
import * as path from 'path';

interface TestResult {
  id: string;
  status: 'pass' | 'fail' | 'skip';
  description?: string;
  error?: string;
  durationMs?: number;
}

interface CoverageUpdate {
  journeyFile: string;
  results: TestResult[];
  timestamp: string;
}

const STATUS_ICONS: Record<string, string> = {
  'pass': '✅',
  'fail': '❌',
  'skip': '⏭️',
  'flaky': '⚠️',
  'wip': '🔄',
};

function parseArgs(): { resultsFile?: string; journeyFile: string; manual?: string } {
  const args = process.argv.slice(2);
  let resultsFile: string | undefined;
  let journeyFile = 'docs/test-coverage/USER-JOURNEYS.md';
  let manual: string | undefined;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--results' && args[i + 1]) {
      resultsFile = args[++i];
    } else if (args[i] === '--journey-file' && args[i + 1]) {
      journeyFile = args[++i];
    } else if (args[i] === '--status' && args[i + 1]) {
      manual = args[++i];
    }
  }

  return { resultsFile, journeyFile, manual };
}

function updateMarkdownTable(content: string, results: TestResult[]): string {
  let updated = content;
  const timestamp = new Date().toISOString().split('T')[0];

  for (const result of results) {
    const icon = STATUS_ICONS[result.status] || '❓';
    
    // Update table rows: | ID | Description | Status | Last Run |
    const tableRowRegex = new RegExp(
      `(\\|\\s*${result.id}\\s*\\|[^|]+\\|)\\s*[^|]+\\s*(\\|[^|]*\\|?)`,
      'g'
    );
    updated = updated.replace(tableRowRegex, `$1 ${icon} | ${timestamp} |`);

    // Update Mermaid diagram markers
    const mermaidRegex = new RegExp(
      `(\\[.*?)(❌|✅|🔄|⚠️)(\\s*${result.id}\\])`,
      'g'
    );
    updated = updated.replace(mermaidRegex, `$1${icon}$3`);
  }

  return updated;
}

function calculateCoverage(content: string): { passed: number; total: number; percentage: number } {
  const passMatches = content.match(/✅/g) || [];
  const failMatches = content.match(/❌/g) || [];
  const wipMatches = content.match(/🔄/g) || [];
  const flakyMatches = content.match(/⚠️/g) || [];

  const passed = passMatches.length;
  const total = passed + failMatches.length + wipMatches.length + flakyMatches.length;
  const percentage = total > 0 ? Math.round((passed / total) * 100) : 0;

  return { passed, total, percentage };
}

function updateCoverageSummary(content: string): string {
  const coverage = calculateCoverage(content);
  
  // Update coverage percentage in summary section
  const summaryRegex = /Coverage:\s*\d+%/g;
  return content.replace(summaryRegex, `Coverage: ${coverage.percentage}%`);
}

async function main() {
  const { resultsFile, journeyFile, manual } = parseArgs();
  
  console.log('🗺️  Pathfinder Coverage Update');
  console.log(`   Journey file: ${journeyFile}`);

  // Read current journey file
  if (!fs.existsSync(journeyFile)) {
    console.error(`❌ Journey file not found: ${journeyFile}`);
    process.exit(1);
  }

  let content = fs.readFileSync(journeyFile, 'utf-8');
  let results: TestResult[] = [];

  // Parse results from file or manual input
  if (resultsFile && fs.existsSync(resultsFile)) {
    const data = JSON.parse(fs.readFileSync(resultsFile, 'utf-8'));
    results = data.results || data;
    console.log(`   Reading from: ${resultsFile}`);
  } else if (manual) {
    // Parse manual format: WELL-01:pass,WELL-02:fail
    results = manual.split(',').map(item => {
      const [id, status] = item.split(':');
      return { id, status: status as 'pass' | 'fail' | 'skip' };
    });
    console.log(`   Manual update: ${results.length} checkpoints`);
  } else {
    // Look for latest results in /tmp
    const tmpDir = '/tmp/test-screenshots';
    if (fs.existsSync(tmpDir)) {
      const dirs = fs.readdirSync(tmpDir).sort().reverse();
      if (dirs.length > 0) {
        const latestResults = path.join(tmpDir, dirs[0], 'results.json');
        if (fs.existsSync(latestResults)) {
          results = JSON.parse(fs.readFileSync(latestResults, 'utf-8'));
          console.log(`   Auto-detected: ${latestResults}`);
        }
      }
    }
  }

  if (results.length === 0) {
    console.log('   No results to update. Use --results or --status');
    process.exit(0);
  }

  // Update content
  content = updateMarkdownTable(content, results);
  content = updateCoverageSummary(content);

  // Write back
  fs.writeFileSync(journeyFile, content);

  // Print summary
  const coverage = calculateCoverage(content);
  console.log(`\n✅ Updated ${results.length} checkpoints`);
  console.log(`📊 Coverage: ${coverage.passed}/${coverage.total} (${coverage.percentage}%)`);
}

main().catch(e => {
  console.error('❌ Update failed:', e.message);
  process.exit(1);
});
