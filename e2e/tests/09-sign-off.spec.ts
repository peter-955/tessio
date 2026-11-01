import { SAVED_CARD_STORY } from "../fake-jira/jira-fixtures.ts";
import { CASE, PROJECT_KEY } from "../support/constants/e2e-project.constant.ts";
import { expect, test } from "../support/fixtures/role-pages.fixture.ts";
import { confirmMarkPassed } from "../support/utils/story-status.util.ts";

test("the QC signs the story off as passed", async ({ qcPage }) => {
  await qcPage.goto(`/projects/${PROJECT_KEY}/stories/${SAVED_CARD_STORY.key}`);
  await confirmMarkPassed(qcPage, SAVED_CARD_STORY.key);
  await expect(qcPage.getByText("Test status is now Passed.")).toBeVisible();
  await expect(qcPage.getByRole("main").getByText("Passed", { exact: true }).first()).toBeVisible();

  await qcPage.getByRole("tab", { name: "Traceability" }).click();
  const traceability = qcPage.getByRole("tabpanel", { name: "Traceability" });
  const criterionRow = traceability.getByRole("row", {
    name: new RegExp(`^${CASE.criterionCode} ${SAVED_CARD_STORY.acceptanceCriteria[0]}`),
  });
  await expect(criterionRow.getByRole("cell").first()).toHaveText("Passed");
  await expect(traceability.getByText("1 passed", { exact: true })).toBeVisible();
});
