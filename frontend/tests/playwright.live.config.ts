import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './specs',
  timeout: 30_000,
  retries: 0,
  use: {
    headless: true,
    viewport: { width: 900, height: 900 },
    deviceScaleFactor: 2, // 200% zoom equivalent
    video: 'off',
    screenshot: 'only-on-failure',
    baseURL: 'https://corvid.contentguru.ai'
  }
});

