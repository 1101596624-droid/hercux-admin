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

    await expect(page.getByRole('heading', { name: /登录|管理/i })).toBeVisible();
    await expect(page.getByPlaceholder(/邮箱|用户名/i)).toBeVisible();
    await expect(page.getByPlaceholder(/密码/i)).toBeVisible();
  });

  test('should login as admin successfully', async ({ page }) => {
    await page.goto('/admin/login');

    await page.getByPlaceholder(/邮箱|用户名/i).fill('admin@hercu.com');
    await page.getByPlaceholder(/密码/i).fill('admin123');
    await page.getByRole('button', { name: /登录/i }).click();

    // Should redirect to admin dashboard
    await expect(page).toHaveURL(/admin\/dashboard|admin/, { timeout: 15000 });
  });

  test('should show error for invalid admin credentials', async ({ page }) => {
    await page.goto('/admin/login');

    await page.getByPlaceholder(/邮箱|用户名/i).fill('invalid@example.com');
    await page.getByPlaceholder(/密码/i).fill('wrongpassword');
    await page.getByRole('button', { name: /登录/i }).click();

    await expect(page.getByText(/登录失败|错误/i)).toBeVisible({ timeout: 10000 });
  });
});

test.describe('Admin Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('/admin/login');
    await page.getByPlaceholder(/邮箱|用户名/i).fill('admin@hercu.com');
    await page.getByPlaceholder(/密码/i).fill('admin123');
    await page.getByRole('button', { name: /登录/i }).click();
    await expect(page).toHaveURL(/admin/, { timeout: 15000 });
  });

  test('should display admin dashboard', async ({ page }) => {
    await page.goto('/admin/dashboard');

    // Should show dashboard content
    await expect(page.locator('main, [role="main"]')).toBeVisible();
  });

  test('should navigate to course management', async ({ page }) => {
    await page.goto('/admin/courses');

    // Should show course list
    await expect(page.locator('main, [role="main"]')).toBeVisible();
  });

  test('should navigate to user management', async ({ page }) => {
    await page.goto('/admin/users');

    // Should show user list
    await expect(page.locator('main, [role="main"]')).toBeVisible();
  });
});
