import { test } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outDir = path.resolve(__dirname, '../../../docs/qa/live');

test.beforeAll(async () => {
  fs.mkdirSync(outDir, { recursive: true });
});

test('live caw at 200% zoom: neutral, mid, end', async ({ page }) => {
  await page.goto('/');
  await page.waitForSelector('div[aria-label="Crow rig"]');
  const crow = page.locator('div[aria-label="Crow rig"]');

  // Ensure neutral
  await page.evaluate(() => (window as any).rig?.reset?.());
  await crow.screenshot({ path: path.join(outDir, 'caw-live-neutral-200.png') });

  // Click Caw CTA
  const cta = page.locator('section.cta');
  await cta.getByRole('button', { name: 'Caw', exact: true }).click();

  // Mid and end frames tuned to ~200ms caw + ~140ms neck thrust
  await page.waitForTimeout(120);
  await crow.screenshot({ path: path.join(outDir, 'caw-live-mid-200.png') });

  await page.waitForTimeout(240);
  await crow.screenshot({ path: path.join(outDir, 'caw-live-end-200.png') });
});

