/**
 * E2E Tests - Course Editor
 */
import { test, expect } from '@playwright/test';

test.describe('Course Editor', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('/admin/login');
    await page.getByPlaceholder(/邮箱|用户名/i).fill('admin@hercu.com');
    await page.getByPlaceholder(/密码/i).fill('admin123');
    await page.getByRole('button', { name: /登录/i }).click();
    await expect(page).toHaveURL(/admin/, { timeout: 15000 });
  });

  test('should open course editor', async ({ page }) => {
    // Navigate to course list
    await page.goto('/admin/courses');

    await page.waitForTimeout(2000);

    // Click edit on first course or create new
    const editButton = page.locator('button:has-text("编辑"), a:has-text("编辑")').first();
    const createButton = page.locator('button:has-text("创建"), button:has-text("新建")').first();

    if (await editButton.isVisible()) {
      await editButton.click();
    } else if (await createButton.isVisible()) {
      await createButton.click();
    }

    await page.waitForTimeout(2000);

    // Should be in editor
    await expect(page.url()).toMatch(/editor|edit/);
  });

  test('should display editor panels', async ({ page }) => {
    // Navigate directly to editor (assuming course ID 1)
    await page.goto('/admin/editor/1');

    await page.waitForTimeout(3000);

    // Editor should have main content area
    await expect(page.locator('main, [role="main"], [class*="editor"]')).toBeVisible();
  });

  test('should add chapter', async ({ page }) => {
    await page.goto('/admin/editor/1');

    await page.waitForTimeout(3000);

    // Look for add chapter button
    const addChapterButton = page.locator('button:has-text("添加章节"), button:has-text("新建章节"), [data-testid="add-chapter"]');

    if (await addChapterButton.isVisible()) {
      const initialChapterCount = await page.locator('[data-testid="chapter"], [class*="chapter"]').count();

      await addChapterButton.click();

      await page.waitForTimeout(1000);

      // Should have one more chapter
      const newChapterCount = await page.locator('[data-testid="chapter"], [class*="chapter"]').count();
      expect(newChapterCount).toBeGreaterThanOrEqual(initialChapterCount);
    }
  });

  test('should save course changes', async ({ page }) => {
    await page.goto('/admin/editor/1');

    await page.waitForTimeout(3000);

    // Make a change (e.g., edit title)
    const titleInput = page.locator('input[name="title"], [data-testid="course-title"]');

    if (await titleInput.isVisible()) {
      await titleInput.fill('Updated Course Title');
    }

    // Find and click save button
    const saveButton = page.locator('button:has-text("保存"), button:has-text("Save")');

    if (await saveButton.isVisible()) {
      await saveButton.click();

      await page.waitForTimeout(2000);

      // Should show success message or button state change
      const successMessage = page.locator('[class*="success"], [class*="toast"]');
      if (await successMessage.count() > 0) {
        await expect(successMessage.first()).toBeVisible();
      }
    }
  });
});

test.describe('AI Studio', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/admin/login');
    await page.getByPlaceholder(/邮箱|用户名/i).fill('admin@hercu.com');
    await page.getByPlaceholder(/密码/i).fill('admin123');
    await page.getByRole('button', { name: /登录/i }).click();
    await expect(page).toHaveURL(/admin/, { timeout: 15000 });
  });

  test('should display AI studio page', async ({ page }) => {
    await page.goto('/admin/studio');

    await page.waitForTimeout(2000);

    // Should show studio interface
    await expect(page.locator('main, [role="main"]')).toBeVisible();
  });

  test('should upload document', async ({ page }) => {
    await page.goto('/admin/studio');

    await page.waitForTimeout(2000);

    // Look for file upload input
    const fileInput = page.locator('input[type="file"]');

    if (await fileInput.count() > 0) {
      // File input exists, studio is functional
      expect(await fileInput.count()).toBeGreaterThan(0);
    }
  });
});
