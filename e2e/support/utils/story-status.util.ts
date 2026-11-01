import { expect, type Page } from "@playwright/test";

export const confirmMarkPassed = async (page: Page, jiraKey: string): Promise<void> => {
  await page.getByRole("button", { name: "Mark passed" }).click();
  const dialog = page.getByRole("dialog", { name: `Mark ${jiraKey} passed?` });
  await dialog.getByRole("button", { name: "Mark passed" }).click();
};

export const expectStoryTestStatus = async (page: Page, statusLabel: string): Promise<void> => {
  await expect(
    page.getByRole("main").getByText(statusLabel, { exact: true }).first(),
  ).toBeVisible();
};
