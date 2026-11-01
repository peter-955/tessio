import type { Locator, Page } from "@playwright/test";

export const selectOption = async (
  page: Page,
  combobox: Locator,
  optionName: string | RegExp,
): Promise<void> => {
  await combobox.click();
  await page.getByRole("option", { name: optionName }).first().click();
};
