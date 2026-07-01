import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/playwright',
  timeout: 30000,
  expect: { timeout: 10000 },
  fullyParallel: false,
  retries: 1,
  use: {
    baseURL: 'http://localhost:5174',
    headless: false,
    viewport: { width: 1350, height: 700 },
    launchOptions: {
      args: [
        '--window-position=0,0',
        '--window-size=1350,700',
        '--no-sandbox',
        '--disable-gpu',
      ],
    },
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],
});
