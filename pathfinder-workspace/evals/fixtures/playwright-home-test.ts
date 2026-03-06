import { test, expect } from "@playwright/test";

test("home page loads", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Welcome" })).toBeVisible();
});

test("navigate to dashboard", async ({ page }) => {
  await page.goto("/");
  await page.click('a[href="/dashboard"]');
  await expect(page).toHaveURL("/dashboard");
});
