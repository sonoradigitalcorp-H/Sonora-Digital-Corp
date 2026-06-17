import { test, expect } from '@playwright/test';

test.describe('SDC App — Spec 009 Verification', () => {

  test('US1: App root serves HTML', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/JARVIS|Sonora|SDC|Mystic/);
  });

  test('US2: User registration returns credentials', async ({ page }) => {
    await page.goto('/app');
    await page.waitForSelector('h2');
    
    const nombre = page.locator('#regNombre');
    const email = page.locator('#regEmail');
    const registerBtn = page.locator('button', { hasText: 'Registrarme' });

    await nombre.fill('Playwright Test');
    await email.fill('pw@test.com');
    await page.selectOption('#regNicho', 'musica');
    await registerBtn.click();

    await expect(page.locator('#credentialsSection')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('#credPassword')).not.toBeEmpty();
    await expect(page.locator('#credApiKey')).not.toBeEmpty();
  });

  test('US3: ABE Music landing loads', async ({ page }) => {
    await page.goto('/static/abe-music.html');
    await expect(page.locator('h1')).toContainText('THE HUB');
    await expect(page).toHaveURL(/abe-music/);
  });

  test('US3: Zamora landing loads', async ({ page }) => {
    await page.goto('/static/zamora.html');
    await expect(page.locator('h1')).toContainText('Alejandro Zamora');
  });

  test('US3: SDC Products landing loads', async ({ page }) => {
    await page.goto('/static/sdc-products.html');
    await expect(page.locator('h1')).toContainText('Sonora Digital Corp');
  });

  test('US4: SPEI payment info available', async ({ page }) => {
    const response = await page.request.get('/api/payments/spei');
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.spei.bank).toBe('NVIO');
    expect(data.spei.clabe).toBe('710969000013788012');
  });

  test('Reporte HTML loads with all sections', async ({ page }) => {
    await page.goto('/static/reporte.html');
    await expect(page.locator('h1')).toContainText('Reporte de Estado');
    const sections = page.locator('h2');
    const count = await sections.count();
    expect(count).toBeGreaterThanOrEqual(5);
  });

});
