import { expect, test, type Page } from "@playwright/test";
import type { PageWidths } from "../types/page-widths.type.ts";

export const readPageWidths = async (page: Page): Promise<PageWidths> =>
  page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: window.innerWidth,
  }));

export const waitForPageToSettle = async (page: Page): Promise<void> => {
  await page.waitForLoadState("networkidle");
  await expect(page.locator('[aria-busy="true"]')).toHaveCount(0);
};

export const expectNoHorizontalScroll = async (page: Page): Promise<void> => {
  await waitForPageToSettle(page);
  const widths = await readPageWidths(page);
  expect
    .soft(widths.scrollWidth, `page scrolls sideways at ${page.url()}`)
    .toBeLessThanOrEqual(widths.innerWidth);
  if (widths.scrollWidth > widths.innerWidth) {
    await page.evaluate(() => {
      window.scrollTo(document.documentElement.scrollWidth, 0);
    });
    await test.info().attach(`sideways scroll ${new URL(page.url()).pathname}`, {
      body: await page.screenshot(),
      contentType: "image/png",
    });
    await page.evaluate(() => {
      window.scrollTo(0, 0);
    });
  }
};
