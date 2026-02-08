#!/usr/bin/env npx tsx
/**
 * Run E2E tests for a user journey
 * 
 * Usage: npx tsx run-tests.ts --journey auth
 *        npx tsx run-tests.ts --file tests/wells.ts
 */

import { chromium, Page, BrowserContext } from 'playwright';
import * as path from 'path';
import * as fs from 'fs';
import { fileURLToPath } from 'url';
import * as dotenv from 'dotenv';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, '../.env.local') });

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const AUTH_STATE_PATH = path.join(__dirname, '../.auth/state.json');

interface TestCase {
  id: string;
  journey: string;
  description: string;
  fn: (page: Page) => Promise<void>;
}

interface TestResult {
  id: string;
  description: string;
  status: 'pass' | 'fail' | 'skip';
  screenshot: string;
  error?: string;
  durationMs: number;
}

export class TestRunner {
  private results: TestResult[] = [];
  private screenshotDir: string;
  private timestamp: string;
  
  constructor() {
    this.timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    this.screenshotDir = `/tmp/test-screenshots/${this.timestamp}`;
    fs.mkdirSync(this.screenshotDir, { recursive: true });
  }
  
  async run(testCases: TestCase[]): Promise<TestResult[]> {
    console.log(`🚀 Running ${testCases.length} tests`);
    console.log(`📸 Screenshots: ${this.screenshotDir}\n`);
    
    // Check auth state exists
    if (!fs.existsSync(AUTH_STATE_PATH)) {
      console.error('❌ No auth state. Run setup-auth.ts first.');
      process.exit(1);
    }
    
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext({ storageState: AUTH_STATE_PATH });
    const page = await context.newPage();
    
    try {
      for (const tc of testCases) {
        await this.runTestCase(page, tc);
      }
    } finally {
      await browser.close();
      this.printSummary();
    }
    
    return this.results;
  }
  
  private async runTestCase(page: Page, tc: TestCase): Promise<void> {
    console.log(`🧪 ${tc.id}: ${tc.description}`);
    const start = Date.now();
    
    try {
      await tc.fn(page);
      
      const screenshot = `${tc.id}-pass.png`;
      await page.screenshot({ 
        path: `${this.screenshotDir}/${screenshot}`, 
        fullPage: true 
      });
      
      this.results.push({
        id: tc.id,
        description: tc.description,
        status: 'pass',
        screenshot,
        durationMs: Date.now() - start,
      });
      console.log(`   ✅ PASS (${Date.now() - start}ms)\n`);
      
    } catch (error: any) {
      const screenshot = `${tc.id}-fail.png`;
      await page.screenshot({ 
        path: `${this.screenshotDir}/${screenshot}`, 
        fullPage: true 
      });
      
      this.results.push({
        id: tc.id,
        description: tc.description,
        status: 'fail',
        screenshot,
        error: error.message,
        durationMs: Date.now() - start,
      });
      console.log(`   ❌ FAIL: ${error.message}\n`);
    }
  }
  
  private printSummary(): void {
    const passed = this.results.filter(r => r.status === 'pass').length;
    const failed = this.results.filter(r => r.status === 'fail').length;
    const total = this.results.length;
    
    console.log('━'.repeat(60));
    console.log('TEST RESULTS');
    console.log('━'.repeat(60));
    console.log(`\n✅ Passed: ${passed}  ❌ Failed: ${failed}  📊 Total: ${total}`);
    console.log(`📈 Pass Rate: ${((passed / total) * 100).toFixed(1)}%`);
    console.log(`📸 Screenshots: ${this.screenshotDir}`);
    
    if (failed > 0) {
      console.log('\n❌ Failed Tests:');
      for (const r of this.results.filter(r => r.status === 'fail')) {
        console.log(`   ${r.id}: ${r.error}`);
      }
    }
  }
}

// Export for use in test files
export { Page, BrowserContext };
export const BASE = BASE_URL;
