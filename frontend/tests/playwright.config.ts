import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './specs',
  timeout: 30_000,
  retries: 0,
  use: {
    headless: true,
    viewport: { width: 900, height: 900 },
    video: 'on',
    screenshot: 'off',
    baseURL: 'http://localhost:4173'
  },
  webServer: {
    command: 'bun run build && bun run preview',
    url: 'http://localhost:4173',
    reuseExistingServer: true,
    timeout: 60_000
  },
});
