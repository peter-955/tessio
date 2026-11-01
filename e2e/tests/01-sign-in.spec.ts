import { expect, test } from "@playwright/test";
import { STORAGE_STATE_PATHS } from "../support/constants/e2e-environment.constant.ts";
import { OWNER } from "../support/constants/e2e-users.constant.ts";
import {
  expectAuthPagesLeft,
  signInWithPassword,
  typeCode,
} from "../support/utils/auth-flow.util.ts";
import { generateTotpCode } from "../support/utils/totp.util.ts";

test("the owner signs in with password and an authenticator code", async ({ page }) => {
  await signInWithPassword(page, OWNER);
  await expect(page.getByRole("heading", { name: "Two-factor authentication" })).toBeVisible();

  await typeCode(page, "Authentication code", "000000");
  await expect(
    page.getByRole("alert").filter({ hasText: "This code is invalid or has already been used." }),
  ).toBeVisible();
  await expect(page).toHaveURL(/\/two-factor(\?|$)/);

  await typeCode(page, "Authentication code", generateTotpCode(OWNER.totpKey));
  await expectAuthPagesLeft(page);

  await page.context().storageState({ path: STORAGE_STATE_PATHS.owner });
});
