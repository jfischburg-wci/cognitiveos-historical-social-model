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

test('live blink at 200% zoom: neutral, mid, end', async ({ page }) => {
  await page.goto('/');
  await page.waitForSelector('div[aria-label="Crow rig"]');
  const crow = page.locator('div[aria-label="Crow rig"]');

  // Ensure neutral
  await page.evaluate(() => (window as any).rig?.reset?.());
  await crow.screenshot({ path: path.join(outDir, 'blink-live-neutral-200.png') });

  // Click Blink CTA
  const cta = page.locator('section.cta');
  await cta.getByRole('button', { name: 'Blink', exact: true }).click();

  // Capture mid and end frames (timing aligned to refined blink)
  await page.waitForTimeout(90);
  await crow.screenshot({ path: path.join(outDir, 'blink-live-mid-200.png') });

  await page.waitForTimeout(200);
  await crow.screenshot({ path: path.join(outDir, 'blink-live-end-200.png') });
});
