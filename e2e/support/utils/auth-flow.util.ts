import { expect, type Page } from "@playwright/test";
import type { E2eUser, E2eUserWithTotpKey, TwoFactorSetupResult } from "../types/e2e-user.type.ts";
import type { TwoFactorSetupPayload } from "../types/two-factor-setup-payload.type.ts";
import { generateTotpCode } from "./totp.util.ts";

const AUTH_PATH_PATTERN = /\/(sign-in|two-factor|invite)(\/|\?|$)/;

export const typeCode = async (page: Page, label: string, code: string): Promise<void> => {
  await page.getByLabel(`${label}, digit 1 of ${code.length}`, { exact: true }).click();
  await page.keyboard.type(code);
};

export const expectAuthPagesLeft = async (page: Page): Promise<void> => {
  await expect(page).not.toHaveURL(AUTH_PATH_PATTERN);
  await expect(page.getByRole("button", { name: "Account menu" })).toBeVisible();
};

export const signInWithPassword = async (page: Page, user: E2eUser): Promise<void> => {
  await page.goto("/sign-in");
  await page.getByRole("textbox", { name: "Email", exact: true }).fill(user.email);
  await page.getByRole("textbox", { name: "Password", exact: true }).fill(user.password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/\/two-factor(\?|$)/);
};

export const signInWithTotp = async (page: Page, user: E2eUserWithTotpKey): Promise<void> => {
  await signInWithPassword(page, user);
  await typeCode(page, "Authentication code", generateTotpCode(user.totpKey));
  await expectAuthPagesLeft(page);
};

export const signOut = async (page: Page): Promise<void> => {
  await page.getByRole("button", { name: "Account menu" }).click();
  await page.getByRole("menuitem", { name: "Sign out", exact: true }).click();
  await expect(page).toHaveURL(/\/sign-in/);
};

export const acceptInviteAndSetUpTwoFactor = async (
  page: Page,
  invitePath: string,
  user: E2eUser,
): Promise<TwoFactorSetupResult> => {
  await page.goto(invitePath);
  await expect(page.getByRole("heading", { name: "Welcome to Tessio" })).toBeVisible();
  await page.getByRole("textbox", { name: "New password", exact: true }).fill(user.password);
  await page.getByRole("textbox", { name: "Confirm password", exact: true }).fill(user.password);
  const setupResponsePromise = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/auth/two-factor/setup") &&
      response.request().method() === "POST" &&
      response.ok(),
  );
  await page.getByRole("button", { name: "Set password" }).click();
  const setupPayload: TwoFactorSetupPayload = await (await setupResponsePromise).json();
  const totpKey = setupPayload.key;
  await expect(
    page.getByRole("heading", { name: "Set up two-factor authentication" }),
  ).toBeVisible();
  await typeCode(page, "Code from the app", generateTotpCode(totpKey));
  const recoveryCodeList = page.getByRole("list", { name: "Recovery codes" });
  await expect(recoveryCodeList).toBeVisible();
  const recoveryCodes = (await recoveryCodeList.getByRole("listitem").allInnerTexts()).map((code) =>
    code.trim(),
  );
  expect(recoveryCodes.length).toBeGreaterThan(0);
  await page.getByLabel("I have saved my recovery codes").check();
  await page.getByRole("button", { name: "Continue" }).click();
  await expectAuthPagesLeft(page);
  return { totpKey, recoveryCodes };
};
