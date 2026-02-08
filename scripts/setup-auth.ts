#!/usr/bin/env npx tsx
/**
 * Auth Setup - Login and save state for reuse
 * 
 * Usage: npx tsx setup-auth.ts
 * 
 * Env vars (in .env.local):
 *   TEST_EMAIL, TEST_PASSWORD, BASE_URL (default: http://localhost:3000)
 */

import { chromium } from 'playwright';
import * as dotenv from 'dotenv';
import * as path from 'path';
import * as fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, '../.env.local') });

const TEST_EMAIL = process.env.TEST_EMAIL;
const TEST_PASSWORD = process.env.TEST_PASSWORD;
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const AUTH_STATE_PATH = path.join(__dirname, '../.auth/state.json');

if (!TEST_EMAIL || !TEST_PASSWORD) {
  console.error('❌ Missing TEST_EMAIL or TEST_PASSWORD in .env.local');
  process.exit(1);
}

async function handleOAuthConsent(page: any): Promise<boolean> {
  if (page.url().includes('auth0.com')) {
    const acceptBtn = page.getByRole('button', { name: 'Accept' });
    if (await acceptBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await acceptBtn.click();
      return true;
    }
  }
  return false;
}

export async function setupAuth(): Promise<string> {
  console.log('🔐 Auth setup...');
  
  // Ensure .auth directory exists
  fs.mkdirSync(path.dirname(AUTH_STATE_PATH), { recursive: true });
  
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Navigate to login
    await page.goto(`${BASE_URL}/auth/login`);
    await page.waitForURL(/auth0|login/, { timeout: 15000 });
    
    // Fill email
    const emailInput = page.locator('input[inputmode="email"], input[type="email"], input[name="email"]').first();
    await emailInput.waitFor({ state: 'visible', timeout: 10000 });
    await emailInput.fill(TEST_EMAIL);
    await page.locator('button[type="submit"]').first().click();
    
    // Fill password
    await page.waitForTimeout(1500);
    await page.locator('input[type="password"]').fill(TEST_PASSWORD);
    await page.locator('button[type="submit"]').first().click();
    
    // Handle OAuth consent if present
    await page.waitForTimeout(3000);
    await handleOAuthConsent(page);
    
    // Wait for redirect to app
    await page.waitForURL(url => url.hostname === 'localhost', { timeout: 30000 });
    await page.waitForLoadState('networkidle');
    
    // Save auth state
    await context.storageState({ path: AUTH_STATE_PATH });
    console.log(`✅ Auth state saved: ${AUTH_STATE_PATH}`);
    
    return AUTH_STATE_PATH;
  } finally {
    await browser.close();
  }
}

// Run if executed directly
setupAuth().catch(e => {
  console.error('❌ Auth setup failed:', e.message);
  process.exit(1);
});
