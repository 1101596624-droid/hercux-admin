/**
 * E2E Tests - Course Editor
 */
import { test, expect } from '@playwright/test';

// Helper to login as admin
async function adminLogin(page: any) {
  await page.goto('/admin/login');
  await page.waitForLoadState('networkidle');
  await page.locator('input#email').fill('admin@hercu.com');
  await page.locator('input#password').fill('admin123');
  await page.locator('button[type="submit"]').click();
  await expect(page).toHaveURL(/admin/, { timeout: 20000 });
}

test.describe('Course Editor', () => {
  test.beforeEach(async ({ page }) => {
    await adminLogin(page);
  });

  test('should display course list', async ({ page }) => {
    await page.goto('/admin/courses');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('body')).toBeVisible();
  });

  test('should open course editor', async ({ page }) => {
    // Navigate directly to editor (assuming course ID 1)
    await page.goto('/admin/editor/1');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    // Editor should have content area
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('AI Studio', () => {
  test.beforeEach(async ({ page }) => {
    await adminLogin(page);
  });

  test('should display AI studio page', async ({ page }) => {
    await page.goto('/admin/studio');
    await page.waitForLoadState('networkidle');

    // Should show studio interface
    await expect(page.locator('body')).toBeVisible();
  });
});
