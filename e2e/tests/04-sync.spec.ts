import {
  ORDER_TRACKING_STORY,
  SAVED_CARD_STORY,
  SUB_TASK_ISSUE_KEY,
} from "../fake-jira/jira-fixtures.ts";
import { PROJECT_KEY } from "../support/constants/e2e-project.constant.ts";
import { expect, test } from "../support/fixtures/role-pages.fixture.ts";

const SYNC_TIMEOUT_MILLISECONDS = 60_000;

test("the owner syncs the sprint stories from Jira", async ({ ownerPage }) => {
  await ownerPage.goto(`/projects/${PROJECT_KEY}/stories`);
  await expect(ownerPage.getByRole("status").filter({ hasText: "Never synced" })).toBeVisible();

  await ownerPage.getByRole("button", { name: "Sync from Jira" }).click();
  await expect(ownerPage.getByRole("status").filter({ hasText: /^Last synced/ })).toBeVisible({
    timeout: SYNC_TIMEOUT_MILLISECONDS,
  });

  const storiesTable = ownerPage.getByRole("table");
  await expect(
    storiesTable.getByRole("row", { name: new RegExp(SAVED_CARD_STORY.key) }),
  ).toContainText(SAVED_CARD_STORY.summary);
  await expect(
    storiesTable.getByRole("row", { name: new RegExp(ORDER_TRACKING_STORY.key) }),
  ).toContainText(ORDER_TRACKING_STORY.summary);
  await expect(storiesTable.getByText(SUB_TASK_ISSUE_KEY, { exact: true })).toHaveCount(0);

  await storiesTable.getByRole("link", { name: SAVED_CARD_STORY.key, exact: true }).click();
  await expect(ownerPage).toHaveURL(new RegExp(`/stories/${SAVED_CARD_STORY.key}$`));
  const criterionItems = ownerPage
    .getByRole("tabpanel", { name: "Overview" })
    .getByRole("listitem")
    .filter({ hasText: /^AC\d+/ });
  await expect(criterionItems).toHaveCount(SAVED_CARD_STORY.acceptanceCriteria.length);
  for (const [index, criterion] of SAVED_CARD_STORY.acceptanceCriteria.entries()) {
    await expect(criterionItems.nth(index)).toContainText(`AC${index + 1}`);
    await expect(criterionItems.nth(index)).toContainText(criterion);
  }
});
