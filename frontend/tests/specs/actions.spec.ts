import { test } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ACTIONS = [
  { name: 'caw', midWait: 350, endWait: 900 },
  { name: 'blink', midWait: 80, endWait: 240 },
  { name: 'headBob', midWait: 450, endWait: 1000 },
  { name: 'preen', midWait: 800, endWait: 1800 },
  { name: 'hop', midWait: 450, endWait: 1000 },
  { name: 'walk', midWait: 320, endWait: 900 },
];

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outRoot = path.resolve(__dirname, '../../../docs/qa/actions-seams-reset-artifacts');

test.beforeAll(async () => {
  fs.mkdirSync(outRoot, { recursive: true });
});

test.describe('Crow actions - mapping, smoothness, reset', () => {
  test('captures screenshots for each action at neutral, mid, end', async ({ page }) => {
    await page.goto('http://localhost:4173/');
    await page.waitForSelector('div[aria-label="Crow rig"]');

    const crow = page.locator('div[aria-label="Crow rig"]');

    for (const a of ACTIONS) {
      await page.evaluate(() => (window as any).rig?.reset?.());
      await crow.screenshot({ path: path.join(outRoot, `${a.name}-neutral.png`) });

      const label = a.name.replace(/([A-Z])/g, ' $1');
      const exact = label.charAt(0).toUpperCase() + label.slice(1);
      const cta = page.locator('section.cta');
      await cta.getByRole('button', { name: exact, exact: true }).click();

      await page.waitForTimeout(a.midWait);
      await crow.screenshot({ path: path.join(outRoot, `${a.name}-mid.png`) });

      await page.waitForTimeout(a.endWait);
      await crow.screenshot({ path: path.join(outRoot, `${a.name}-end.png`) });
    }
  });
});
