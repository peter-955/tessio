import { expect, type Page } from "@playwright/test";

const RECORD_PATH_PATTERN = /\/runs\/([^/]+)\/record$/;

export const readRunIdFromRecordUrl = (page: Page): string => {
  const runId = RECORD_PATH_PATTERN.exec(new URL(page.url()).pathname)?.[1];
  if (runId === undefined) {
    throw new Error(`Not on a record page: ${page.url()}`);
  }
  return runId;
};

export const recordStep = async (
  page: Page,
  order: number,
  statusLabel: string,
  actualResult?: string,
): Promise<void> => {
  const stepStatus = page.getByRole("radiogroup", { name: `Step ${order} status` });
  await stepStatus.getByText(statusLabel, { exact: true }).click();
  await expect(stepStatus.getByRole("radio", { name: statusLabel, exact: true })).toBeChecked();
  if (actualResult !== undefined) {
    await page
      .getByRole("listitem")
      .filter({ has: stepStatus })
      .getByRole("textbox", { name: "Actual result" })
      .fill(actualResult);
  }
};

export const saveCaseResult = async (page: Page, caseCode: string): Promise<void> => {
  await page.getByRole("button", { name: "Save result" }).click();
  await expect(page.getByText(`Result saved for ${caseCode}`)).toBeVisible();
};

export const finishRun = async (page: Page): Promise<void> => {
  await page.getByRole("button", { name: "Finish run" }).click();
  const dialog = page.getByRole("dialog", { name: "Finish manual run" });
  await dialog.getByRole("button", { name: "Finish run" }).click();
  await expect(page.getByText("Run finished")).toBeVisible();
};

export const expectRunStatus = async (page: Page, statusLabel: string): Promise<void> => {
  const statusTerm = page.getByRole("term").filter({ hasText: /^Status$/ });
  await expect(statusTerm.locator("xpath=following-sibling::*[1]")).toHaveText(statusLabel);
};
