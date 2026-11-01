import type { Browser, Page } from "@playwright/test";
import { STORAGE_STATE_PATHS } from "../support/constants/e2e-environment.constant.ts";
import { DEV, QC } from "../support/constants/e2e-users.constant.ts";
import { expect, test } from "../support/fixtures/role-pages.fixture.ts";
import type { E2eUser } from "../support/types/e2e-user.type.ts";
import {
  acceptInviteAndSetUpTwoFactor,
  expectAuthPagesLeft,
  signInWithPassword,
  signOut,
} from "../support/utils/auth-flow.util.ts";
import { waitForInvitePath } from "../support/utils/mailpit.util.ts";
import { mergeRunState, requireRunValue } from "../support/utils/run-state.util.ts";

const inviteMember = async (ownerPage: Page, user: E2eUser): Promise<void> => {
  await ownerPage.getByRole("button", { name: "Invite user" }).click();
  const dialog = ownerPage.getByRole("dialog", { name: "Invite a user" });
  await dialog.getByRole("textbox", { name: "Email" }).fill(user.email);
  await dialog.getByRole("textbox", { name: "Name" }).fill(user.name);
  await expect(dialog.getByRole("combobox", { name: "Workspace role" })).toHaveValue("Member");
  await dialog.getByRole("button", { name: "Send invite" }).click();
  await expect(ownerPage.getByText(`Invite sent to ${user.email}`)).toBeVisible();
  await expect(dialog).toBeHidden();
  await expect(ownerPage.getByRole("row", { name: new RegExp(user.email) })).toContainText(
    "Invited",
  );
};

const acceptInvite = async (
  browser: Browser,
  user: E2eUser,
  storageStatePath: string,
): Promise<string[]> => {
  const context = await browser.newContext();
  const page = await context.newPage();
  const invitePath = await waitForInvitePath(user.email);
  const setup = await acceptInviteAndSetUpTwoFactor(page, invitePath, user);
  await context.storageState({ path: storageStatePath });
  await context.close();
  return setup.recoveryCodes;
};

test("the owner invites a QC and a developer who set up two-factor", async ({
  browser,
  ownerPage,
}) => {
  await ownerPage.goto("/users");
  await expect(ownerPage.getByRole("heading", { name: "Users", level: 1 })).toBeVisible();

  await inviteMember(ownerPage, QC);
  await inviteMember(ownerPage, DEV);

  const qcRecoveryCodes = await acceptInvite(browser, QC, STORAGE_STATE_PATHS.qc);
  await acceptInvite(browser, DEV, STORAGE_STATE_PATHS.dev);
  mergeRunState({ qcRecoveryCodes });

  await ownerPage.reload();
  await expect(ownerPage.getByRole("row", { name: new RegExp(QC.email) })).toContainText("Active");
  await expect(ownerPage.getByRole("row", { name: new RegExp(DEV.email) })).toContainText("Active");
});

test("the QC signs in again with a recovery code", async ({ qcPage }) => {
  await qcPage.goto("/projects");
  await signOut(qcPage);

  const [recoveryCode] = requireRunValue("qcRecoveryCodes");
  expect(recoveryCode).toBeDefined();
  await signInWithPassword(qcPage, QC);
  await qcPage.getByRole("button", { name: "Use a recovery code instead" }).click();
  await qcPage.getByRole("textbox", { name: "Recovery code" }).fill(recoveryCode ?? "");
  await qcPage.getByRole("button", { name: "Verify" }).click();
  await expectAuthPagesLeft(qcPage);

  await qcPage.context().storageState({ path: STORAGE_STATE_PATHS.qc });
});
