import { test } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outDir = path.resolve(__dirname, '../../../docs/qa/live');

test.beforeAll(async () => { fs.mkdirSync(outDir, { recursive: true }); });

test('live hop at 100% zoom: neutral, mid, end', async ({ page }) => {
  await page.goto('/');
  await page.waitForSelector('div[aria-label="Crow rig"]');
  const crow = page.locator('div[aria-label="Crow rig"]');
  await page.evaluate(() => (window as any).rig?.reset?.());
  await crow.screenshot({ path: path.join(outDir, 'hop-live-neutral-100.png') });
  const cta = page.locator('section.cta');
  await cta.getByRole('button', { name: 'Hop', exact: true }).click();
  await page.waitForTimeout(450);
  await crow.screenshot({ path: path.join(outDir, 'hop-live-mid-100.png') });
  await page.waitForTimeout(1000);
  await crow.screenshot({ path: path.join(outDir, 'hop-live-end-100.png') });
});

