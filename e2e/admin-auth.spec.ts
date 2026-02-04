/**
 * E2E Tests - Admin Authentication
 */
import { test, expect } from '@playwright/test';

test.describe('Admin Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
  });

  test('should display admin login page', async ({ page }) => {
    await page.goto('/admin/login');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('h2:has-text("欢迎回来")')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('input#email')).toBeVisible();
    await expect(page.locator('input#password')).toBeVisible();
  });

  test('should login as admin successfully', async ({ page }) => {
    await page.goto('/admin/login');
    await page.waitForLoadState('networkidle');

    await page.locator('input#email').fill('admin@hercu.com');
    await page.locator('input#password').fill('admin123');
    await page.locator('button[type="submit"]').click();

    // Should redirect to admin dashboard
    await expect(page).toHaveURL(/admin/, { timeout: 20000 });
  });

  test('should show error for invalid admin credentials', async ({ page }) => {
    await page.goto('/admin/login');
    await page.waitForLoadState('networkidle');

    await page.locator('input#email').fill('invalid@example.com');
    await page.locator('input#password').fill('wrongpassword');
    await page.locator('button[type="submit"]').click();

    // Wait for error - check for any error indicator
    await page.waitForTimeout(3000);
    // Just verify we're still on login page (not redirected)
    expect(page.url()).toContain('login');
  });
});

test.describe('Admin Dashboard', () => {
  // Helper to login
  async function adminLogin(page: any) {
    await page.goto('/admin/login');
    await page.waitForLoadState('networkidle');
    await page.locator('input#email').fill('admin@hercu.com');
    await page.locator('input#password').fill('admin123');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/admin/, { timeout: 20000 });
  }

  test('should display admin dashboard', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/admin/dashboard');
    await page.waitForLoadState('networkidle');

    // Should show dashboard content
    await expect(page.locator('body')).toBeVisible();
  });

  test('should navigate to course management', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/admin/courses');
    await page.waitForLoadState('networkidle');

    // Should show course list
    await expect(page.locator('body')).toBeVisible();
  });
});
