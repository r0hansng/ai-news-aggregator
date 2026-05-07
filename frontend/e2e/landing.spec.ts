import { test, expect } from '@playwright/test';

test('landing page has title and onboarding button', async ({ page }) => {
  await page.goto('/');
  
  // Check for the main brand title
  await expect(page.locator('h1')).toContainText('AI Digest');
  
  // Check for the "Start Your Signal" or equivalent button
  const startButton = page.getByRole('button', { name: /start|onboard|get started/i });
  await expect(startButton).toBeVisible();
});
