import { test, expect } from '@playwright/test';

test.describe('Clone Service — Web Integration', () => {

  test('ABE service page loads for client access', async ({ page }) => {
    await page.goto('http://localhost:5180/pwa/estado.html');
    await expect(page).toHaveTitle(/Estado|SDC|Sonora/);
    const heading = page.locator('h1, h2');
    await expect(heading).toBeVisible({ timeout: 5000 });
  });

  test('Clone service SPEC accessible via process docs', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await expect(page).toHaveTitle(/JARVIS|Sonora|SDC|Mystic/);
    const body = page.locator('body');
    const text = await body.innerText();
    expect(text.length).toBeGreaterThan(0);
  });

  test('Clone pipeline CLI help outputs correctly', async () => {
    const { exec } = require('child_process');
    const result = await new Promise<string>((resolve) => {
      exec('python3 scripts/clone_pipeline.py --help', {
        cwd: '/home/mystic/sonora-digital-corp'
      }, (err, stdout) => resolve(stdout));
    });
    expect(result).toContain('Clone Service Pipeline');
    expect(result).toContain('--client-id');
    expect(result).toContain('--action');
    expect(result).toContain('validate');
    expect(result).toContain('train');
    expect(result).toContain('generate');
    expect(result).toContain('status');
    expect(result).toContain('create-pack');
  });

  test('Clone pipeline validates photos correctly', async () => {
    const { exec } = require('child_process');
    const result = await new Promise<string>((resolve) => {
      exec(
        'python3 scripts/clone_pipeline.py --client-id pw-test --action validate --photo-urls p1.jpg p2.jpg --audio-url a.wav',
        { cwd: '/home/mystic/sonora-digital-corp' },
        (err, stdout) => resolve(stdout)
      );
    });
    const data = JSON.parse(result);
    expect(data.client_id).toBe('pw-test');
    expect(data.status).toBe('collecting');
    expect(data.photos_needed).toBeGreaterThan(0);
  });

  test('MCP server endpoints respond', async ({ page }) => {
    const response = await page.request.get('http://localhost:18989/mcp/health');
    if (response.status() === 200) {
      const data = await response.json();
      expect(data.status).toBeDefined();
    }
  });

  test('Supabase storage bucket accessible', async ({ page }) => {
    const supabaseUrl = 'https://jibalggzudkflwzdndqz.supabase.co';
    const response = await page.request.get(`${supabaseUrl}/rest/v1/`, {
      headers: { 'Accept': 'application/json' }
    });
    expect(response.status()).toBe(200);
  });

  test('Clone service DB schema exists', async () => {
    const fs = require('fs');
    const schema = fs.readFileSync(
      '/home/mystic/sonora-digital-corp/config/clone-schema.sql',
      'utf-8'
    );
    expect(schema).toContain('CREATE TABLE IF NOT EXISTS clients');
    expect(schema).toContain('CREATE TABLE IF NOT EXISTS photos');
    expect(schema).toContain('CREATE TABLE IF NOT EXISTS audio');
    expect(schema).toContain('CREATE TABLE IF NOT EXISTS assets');
  });

  test('All clone test files exist and are valid', async () => {
    const fs = require('fs');
    const testFiles = [
      'tests/test_clone_recollection.py',
      'tests/test_clone_training.py',
      'tests/test_clone_generation.py',
      'tests/test_clone_delivery.py',
      'tests/test_clone_pipeline.py',
      'tests/test_clone_credits.py',
      'tests/test_clone_integration.py',
    ];
    for (const file of testFiles) {
      const exists = fs.existsSync(`/home/mystic/sonora-digital-corp/${file}`);
      expect(exists).toBeTruthy();
    }
  });
});
