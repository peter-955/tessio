import { SAVED_CARD_STORY } from "../fake-jira/jira-fixtures.ts";
import {
  CASE,
  ENVIRONMENT,
  FAILED_STEP_ACTUAL_RESULT,
  PROJECT_KEY,
} from "../support/constants/e2e-project.constant.ts";
import { expect, test } from "../support/fixtures/role-pages.fixture.ts";
import {
  expectRunStatus,
  finishRun,
  readRunIdFromRecordUrl,
  recordStep,
  saveCaseResult,
} from "../support/utils/manual-run.util.ts";
import { mergeRunState, requireRunValue } from "../support/utils/run-state.util.ts";
import { selectOption } from "../support/utils/select-option.util.ts";

test("the QC records a manual run where the second step fails", async ({ qcPage }) => {
  const caseCode = requireRunValue("caseCode");
  await qcPage.goto(`/projects/${PROJECT_KEY}/runs/new`);
  await selectOption(
    qcPage,
    qcPage.getByRole("combobox", { name: "Story" }),
    new RegExp(SAVED_CARD_STORY.key),
  );
  await expect(qcPage.getByRole("combobox", { name: "Environment" })).toHaveValue(ENVIRONMENT.name);
  await expect(
    qcPage.getByRole("checkbox", { name: new RegExp(`^${caseCode} · ${CASE.title}`) }),
  ).toBeChecked();
  await qcPage.getByRole("button", { name: "Start manual run" }).click();

  await expect(qcPage).toHaveURL(/\/record$/);
  const firstRunId = readRunIdFromRecordUrl(qcPage);
  mergeRunState({ firstRunId });
  await expect(
    qcPage.getByRole("heading", { name: `Manual run · ${SAVED_CARD_STORY.key}`, level: 1 }),
  ).toBeVisible();

  await recordStep(qcPage, 1, "Passed");
  await recordStep(qcPage, 2, "Failed", FAILED_STEP_ACTUAL_RESULT);
  await saveCaseResult(qcPage, caseCode);
  await expect(qcPage.getByText(/1 of 1 cases recorded/)).toBeVisible();
  await finishRun(qcPage);

  await qcPage.goto(`/projects/${PROJECT_KEY}/runs/${firstRunId}`);
  await expect(
    qcPage.getByRole("heading", { name: `Run on ${SAVED_CARD_STORY.key}`, level: 1 }),
  ).toBeVisible();
  await expectRunStatus(qcPage, "Failed");
  await expect(
    qcPage
      .getByRole("list", { name: `Steps of ${caseCode}` })
      .getByRole("listitem")
      .nth(1),
  ).toContainText(FAILED_STEP_ACTUAL_RESULT);

  await qcPage.goto(`/projects/${PROJECT_KEY}/stories/${SAVED_CARD_STORY.key}`);
  await expect(qcPage.getByRole("main").getByText("In test", { exact: true })).toBeVisible();
});
