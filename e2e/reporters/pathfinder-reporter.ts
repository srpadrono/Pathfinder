/**
 * Pathfinder Reporter
 *
 * Custom Playwright reporter that extracts checkpoint IDs from test titles
 * and writes structured results for trail map updates.
 *
 * Test titles must follow the format: "CHECKPOINT-ID: Description"
 * Example: "AUTH-01: Login redirects to dashboard"
 *
 * Outputs: test-results/checkpoints.json
 */

import type {
  Reporter,
  TestCase,
  TestResult,
  FullResult,
  Suite,
} from '@playwright/test/reporter';
import * as fs from 'fs';

interface CheckpointResult {
  id: string;
  description: string;
  status: 'pass' | 'fail' | 'skip';
  durationMs: number;
  error?: string;
  journey?: string;
}

class PathfinderReporter implements Reporter {
  private checkpoints: Map<string, CheckpointResult> = new Map();
  private startTime: number = Date.now();

  onBegin(_config: unknown, _suite: Suite) {
    this.startTime = Date.now();
    console.log('\n🗺️  Pathfinder Trail Reporter');
    console.log('━'.repeat(50));
  }

  onTestEnd(test: TestCase, result: TestResult) {
    // Extract checkpoint ID from test title: "AUTH-01: Login redirects"
    const match = test.title.match(/^([A-Z]+-\d+):\s*(.+)/);
    if (!match) return;

    const [, id, description] = match;

    // Extract journey from describe block or file name
    const journey = test.parent?.title || test.location.file.match(/([^/]+)\.spec\.ts$/)?.[1] || 'unknown';

    const status: 'pass' | 'fail' | 'skip' =
      result.status === 'passed' ? 'pass' :
      result.status === 'skipped' ? 'skip' : 'fail';

    this.checkpoints.set(id, {
      id,
      description,
      status,
      durationMs: result.duration,
      error: result.error?.message,
      journey,
    });

    const marker = status === 'pass' ? '✅' : status === 'skip' ? '⏭️' : '❌';
    console.log(`  ${marker} ${id}: ${description} (${result.duration}ms)`);
  }

  onEnd(result: FullResult) {
    const checkpointsArray = Array.from(this.checkpoints.values());
    const passed = checkpointsArray.filter((c) => c.status === 'pass').length;
    const failed = checkpointsArray.filter((c) => c.status === 'fail').length;
    const skipped = checkpointsArray.filter((c) => c.status === 'skip').length;
    const total = checkpointsArray.length;
    const coverage = total > 0 ? Math.round((passed / total) * 100) : 0;

    // Write structured JSON output
    const output = {
      timestamp: new Date().toISOString(),
      durationMs: Date.now() - this.startTime,
      status: result.status,
      summary: { passed, failed, skipped, total, coverage },
      checkpoints: Object.fromEntries(
        checkpointsArray.map((c) => [c.id, c])
      ),
    };

    fs.mkdirSync('test-results', { recursive: true });
    fs.writeFileSync(
      'test-results/checkpoints.json',
      JSON.stringify(output, null, 2)
    );

    // Print summary
    console.log('\n' + '━'.repeat(50));
    console.log('🗺️  TRAIL MAP SUMMARY');
    console.log('━'.repeat(50));
    console.log(`  ✅ Cleared: ${passed}`);
    console.log(`  ❌ Blocked: ${failed}`);
    console.log(`  ⏭️  Skipped: ${skipped}`);
    console.log(`  📊 Coverage: ${coverage}% (${passed}/${total})`);
    console.log(`  📁 Results: test-results/checkpoints.json`);

    if (failed > 0) {
      console.log('\n  ❌ Blocked Checkpoints:');
      for (const c of checkpointsArray.filter((c) => c.status === 'fail')) {
        console.log(`     ${c.id}: ${c.error || 'Unknown error'}`);
      }
    }

    console.log('━'.repeat(50) + '\n');
  }
}

export default PathfinderReporter;
