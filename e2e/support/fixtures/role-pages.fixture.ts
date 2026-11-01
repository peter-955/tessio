import {
  test as base,
  type Browser,
  type BrowserContextOptions,
  type Page,
} from "@playwright/test";
import { STORAGE_STATE_PATHS } from "../constants/e2e-environment.constant.ts";

interface RolePages {
  ownerPage: Page;
  qcPage: Page;
  devPage: Page;
}

const openRolePage = async (
  browser: Browser,
  contextOptions: BrowserContextOptions,
  storageStatePath: string,
  use: (page: Page) => Promise<void>,
): Promise<void> => {
  const context = await browser.newContext({ ...contextOptions, storageState: storageStatePath });
  const page = await context.newPage();
  await use(page);
  await context.close();
};

export const test = base.extend<RolePages>({
  ownerPage: async ({ browser, baseURL, viewport, colorScheme, locale }, use) => {
    await openRolePage(
      browser,
      { baseURL, viewport, colorScheme, locale },
      STORAGE_STATE_PATHS.owner,
      use,
    );
  },
  qcPage: async ({ browser, baseURL, viewport, colorScheme, locale }, use) => {
    await openRolePage(
      browser,
      { baseURL, viewport, colorScheme, locale },
      STORAGE_STATE_PATHS.qc,
      use,
    );
  },
  devPage: async ({ browser, baseURL, viewport, colorScheme, locale }, use) => {
    await openRolePage(
      browser,
      { baseURL, viewport, colorScheme, locale },
      STORAGE_STATE_PATHS.dev,
      use,
    );
  },
});

export { expect } from "@playwright/test";
