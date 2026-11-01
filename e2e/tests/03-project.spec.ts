import { FAKE_JIRA_SITE_URL } from "../support/constants/e2e-environment.constant.ts";
import {
  ENVIRONMENT,
  JIRA_API_TOKEN,
  JIRA_USER_EMAIL,
  PROJECT_KEY,
  PROJECT_NAME,
} from "../support/constants/e2e-project.constant.ts";
import { DEV, QC } from "../support/constants/e2e-users.constant.ts";
import { JIRA_ACCOUNT, JIRA_BOARD } from "../fake-jira/jira-fixtures.ts";
import { expect, test } from "../support/fixtures/role-pages.fixture.ts";
import type { E2eUser } from "../support/types/e2e-user.type.ts";
import { selectOption } from "../support/utils/select-option.util.ts";
import type { Page } from "@playwright/test";

const addMember = async (ownerPage: Page, user: E2eUser, roleName: string): Promise<void> => {
  await ownerPage.getByRole("button", { name: "Add member" }).click();
  const dialog = ownerPage.getByRole("dialog", { name: "Add member" });
  await selectOption(
    ownerPage,
    dialog.getByRole("combobox", { name: "User" }),
    new RegExp(user.name),
  );
  await selectOption(ownerPage, dialog.getByRole("combobox", { name: "Role" }), roleName);
  await dialog.getByRole("button", { name: "Add", exact: true }).click();
  await expect(ownerPage.getByText("Member added")).toBeVisible();
  await expect(ownerPage.getByRole("row", { name: new RegExp(user.name) })).toBeVisible();
};

test("the owner connects Jira", async ({ ownerPage }) => {
  await ownerPage.goto("/settings");
  await ownerPage.getByRole("textbox", { name: "Site URL" }).fill(FAKE_JIRA_SITE_URL);
  await ownerPage.getByRole("textbox", { name: "Jira user email" }).fill(JIRA_USER_EMAIL);
  await ownerPage.getByRole("textbox", { name: "API token" }).fill(JIRA_API_TOKEN);
  await ownerPage.getByRole("button", { name: "Test and save" }).click();
  await expect(ownerPage.getByText(`Jira connected as ${JIRA_ACCOUNT.displayName}`)).toBeVisible();
  await expect(ownerPage.getByText("Connected", { exact: true })).toBeVisible();
});

test("the owner creates the SHOP project and adds members", async ({ ownerPage }) => {
  await ownerPage.goto("/projects/new");
  await expect(ownerPage.getByRole("heading", { name: "New project", level: 1 })).toBeVisible();
  await selectOption(
    ownerPage,
    ownerPage.getByRole("combobox", { name: "Jira project" }),
    new RegExp(PROJECT_NAME),
  );
  await selectOption(
    ownerPage,
    ownerPage.getByRole("combobox", { name: "Jira board" }),
    JIRA_BOARD.name,
  );
  await ownerPage.getByRole("textbox", { name: "Name", exact: true }).fill(PROJECT_NAME);
  await ownerPage.getByRole("textbox", { name: "Key", exact: true }).fill(PROJECT_KEY);
  await ownerPage.getByRole("button", { name: "Create project" }).click();
  await expect(ownerPage.getByText("Project created")).toBeVisible();
  await expect(ownerPage).toHaveURL(new RegExp(`/projects/${PROJECT_KEY}`));

  await ownerPage.goto(`/projects/${PROJECT_KEY}/members`);
  await expect(ownerPage.getByRole("heading", { name: "Members", level: 1 })).toBeVisible();
  await addMember(ownerPage, QC, "QC");
  await addMember(ownerPage, DEV, "Dev");
});

test("the QC adds the Staging environment", async ({ qcPage }) => {
  await qcPage.goto(`/projects/${PROJECT_KEY}/test-data?tab=environments`);
  await qcPage.getByRole("button", { name: "Add environment" }).first().click();
  const dialog = qcPage.getByRole("dialog", { name: "Add environment" });
  await dialog.getByRole("textbox", { name: "Name" }).fill(ENVIRONMENT.name);
  await dialog.getByRole("textbox", { name: "Base URL" }).fill(ENVIRONMENT.url);
  await dialog.getByRole("button", { name: "Create environment" }).click();
  await expect(qcPage.getByText("Environment created")).toBeVisible();
  await expect(
    qcPage
      .getByRole("table", { name: "Environments" })
      .getByRole("row", { name: new RegExp(ENVIRONMENT.name) }),
  ).toBeVisible();
});
