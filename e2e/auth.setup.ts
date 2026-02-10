import { test as setup } from '@playwright/test';
import * as fs from 'fs';

const AUTH_FILE = '.auth/state.json';

setup('authenticate', async ({ page }) => {
  // Ensure .auth directory exists
  fs.mkdirSync('.auth', { recursive: true });

  const email = process.env.TEST_EMAIL;
  const password = process.env.TEST_PASSWORD;

  if (!email || !password) {
    throw new Error('Missing TEST_EMAIL or TEST_PASSWORD in .env.local');
  }

  // Navigate to login
  await page.goto('/auth/login');

  // Fill email — auto-wait for element, no arbitrary timeout
  const emailInput = page.locator('input[type="email"], input[inputmode="email"], input[name="email"]').first();
  await emailInput.fill(email);
  await page.locator('button[type="submit"]').first().click();

  // Fill password — Playwright auto-waits for visibility
  await page.locator('input[type="password"]').fill(password);
  await page.locator('button[type="submit"]').first().click();

  // Handle OAuth consent if present (Auth0, etc.)
  const acceptBtn = page.getByRole('button', { name: 'Accept' });
  if (await acceptBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
    await acceptBtn.click();
  }

  // Wait for redirect to app
  await page.waitForURL((url) => !url.hostname.includes('auth0'), { timeout: 30000 });
  await page.waitForLoadState('networkidle');

  // Save auth state
  await page.context().storageState({ path: AUTH_FILE });
});
