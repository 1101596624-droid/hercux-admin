/**
 * Admin Component Lifecycle Tests
 * Tests rapid navigation and resource cleanup in admin panel
 */
import { test, expect } from '@playwright/test';

// Helper to login as admin
async function loginAsAdmin(page: any) {
  await page.goto('/admin/login');
  await page.waitForLoadState('domcontentloaded');
  await page.locator('input#email').fill('admin@hercu.com');
  await page.locator('input#password').fill('admin123');
  await page.locator('button[type="submit"]').click();
  await expect(page).toHaveURL(/admin\/dashboard/, { timeout: 15000 });
}

test.describe('Admin Component Lifecycle', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('should handle rapid admin page navigation', async ({ page }) => {
    const errors: string[] = [];
    
    page.on('pageerror', (error) => {
      errors.push(error.message);
    });

    // Navigate through admin pages rapidly
    const adminPages = [
      '/admin/dashboard',
      '/admin/courses',
      '/admin/users',
      '/admin/studio',
      '/admin/dashboard'
    ];
    
    for (const path of adminPages) {
      await page.goto(path);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(300);
    }

    // Filter critical errors
    const criticalErrors = errors.filter(e => 
      e.includes('Cannot read properties') ||
      e.includes('texture') ||
      e.includes('undefined')
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test('should cleanup studio resources on navigation', async ({ page }) => {
    const errors: string[] = [];
    
    page.on('pageerror', (error) => {
      if (error.message.includes('texture') || 
          error.message.includes('WebGL') ||
          error.message.includes('Cannot read properties of undefined')) {
        errors.push(error.message);
      }
    });

    // Navigate to studio and back multiple times
    for (let i = 0; i < 3; i++) {
      await page.goto('/admin/studio');
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(500);
      await page.goto('/admin/dashboard');
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(500);
    }

    expect(errors).toHaveLength(0);
  });

  test('should handle course editor navigation', async ({ page }) => {
    // Go to courses list
    await page.goto('/admin/courses');
    await page.waitForLoadState('domcontentloaded');
    
    // Check if there are courses
    const courseLinks = page.locator('a[href*="/admin/editor/"]');
    const count = await courseLinks.count();
    
    if (count > 0) {
      // Click first course editor link
      await courseLinks.first().click();
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(1000);
      
      // Navigate back
      await page.goto('/admin/courses');
      await page.waitForLoadState('domcontentloaded');
      
      // Should not crash
      await expect(page.locator('main')).toBeVisible({ timeout: 10000 });
    }
  });
});

test.describe('Admin Error Handling', () => {
  test('should redirect to login for unauthenticated access', async ({ page }) => {
    // Clear any existing session
    await page.goto('/admin/login');
    await page.evaluate(() => localStorage.clear());
    
    // Try to access protected page
    await page.goto('/admin/dashboard');
    await page.waitForLoadState('domcontentloaded');
    
    // Should redirect to login
    await expect(page).toHaveURL(/admin\/login/, { timeout: 10000 });
  });
});
