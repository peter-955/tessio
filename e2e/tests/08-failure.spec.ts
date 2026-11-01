import { SAVED_CARD_STORY } from "../fake-jira/jira-fixtures.ts";
import { CASE, PROJECT_KEY } from "../support/constants/e2e-project.constant.ts";
import { DEV } from "../support/constants/e2e-users.constant.ts";
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
import { confirmMarkPassed } from "../support/utils/story-status.util.ts";

const STORY_PATH = `/projects/${PROJECT_KEY}/stories/${SAVED_CARD_STORY.key}`;
const FAILURE_PATH_PATTERN = new RegExp(`/projects/${PROJECT_KEY}/failures/([^/]+)$`);

const failurePath = (): string =>
  `/projects/${PROJECT_KEY}/failures/${requireRunValue("failureId")}`;

const failureLinkName = (caseCode: string): string => `${caseCode} · ${CASE.title}`;

test("an open failure blocks the story sign-off", async ({ qcPage }) => {
  await qcPage.goto(STORY_PATH);
  await confirmMarkPassed(qcPage, SAVED_CARD_STORY.key);
  await expect(
    qcPage.getByText("Resolve active failures and wait for running runs before marking it passed."),
  ).toBeVisible();
  await expect(qcPage.getByRole("main").getByText("In test", { exact: true })).toBeVisible();
});

test("the QC assigns the failure to the developer", async ({ qcPage }) => {
  const caseCode = requireRunValue("caseCode");
  await qcPage.goto(`/projects/${PROJECT_KEY}/failures`);
  const failureRow = qcPage
    .getByRole("table", { name: "Failures" })
    .getByRole("row", { name: new RegExp(`^${caseCode} · `) });
  await expect(failureRow.getByRole("cell", { name: "Open", exact: true })).toBeVisible();
  await failureRow.getByRole("link", { name: failureLinkName(caseCode) }).click();

  await expect(qcPage).toHaveURL(FAILURE_PATH_PATTERN);
  const failureId = FAILURE_PATH_PATTERN.exec(new URL(qcPage.url()).pathname)?.[1];
  expect(failureId).toBeDefined();
  mergeRunState({ failureId: failureId ?? "" });

  await qcPage.getByRole("button", { name: "Assign" }).click();
  const dialog = qcPage.getByRole("dialog", { name: "Assign failure" });
  await selectOption(
    qcPage,
    dialog.getByRole("combobox", { name: "Assignee" }),
    new RegExp(DEV.name),
  );
  await dialog.getByRole("button", { name: "Save" }).click();
  await expect(qcPage.getByText(`${caseCode} assigned to ${DEV.name}.`)).toBeVisible();
});

test("the developer marks the failure fixed", async ({ devPage }) => {
  const caseCode = requireRunValue("caseCode");
  await devPage.goto(failurePath());
  await expect(devPage.getByRole("main").getByText(DEV.name).first()).toBeVisible();
  await devPage.getByRole("button", { name: "Mark fixed" }).click();
  await expect(devPage.getByText(`${caseCode} is now Fixed.`)).toBeVisible();
});

test("the QC re-runs the failed case, it passes and the failure is verified", async ({
  qcPage,
}) => {
  const caseCode = requireRunValue("caseCode");
  const firstRunId = requireRunValue("firstRunId");
  await qcPage.goto(`/projects/${PROJECT_KEY}/runs/${firstRunId}`);
  await qcPage.getByRole("button", { name: "Re-run failed (1)" }).click();
  const dialog = qcPage.getByRole("dialog", { name: "Re-run failed cases manually" });
  await expect(dialog.getByRole("combobox", { name: "Environment" })).toHaveValue(
    "Same as original run",
  );
  await dialog.getByRole("button", { name: "Start re-run" }).click();
  await expect(qcPage.getByText("Re-run started")).toBeVisible();

  await expect(qcPage).toHaveURL(/\/record$/);
  const rerunId = readRunIdFromRecordUrl(qcPage);
  expect(rerunId).not.toBe(firstRunId);
  mergeRunState({ rerunId });
  await recordStep(qcPage, 1, "Passed");
  await recordStep(qcPage, 2, "Passed");
  await saveCaseResult(qcPage, caseCode);
  await finishRun(qcPage);

  await qcPage.goto(`/projects/${PROJECT_KEY}/runs/${rerunId}`);
  await expectRunStatus(qcPage, "Passed");
  await expect(qcPage.getByText("Re-run of an earlier run")).toBeVisible();

  await qcPage.goto(failurePath());
  await expect(qcPage.getByRole("main").getByText("Fixed", { exact: true }).first()).toBeVisible();
  await qcPage.getByRole("button", { name: "Verify" }).click();
  await expect(qcPage.getByText(`${caseCode} is now Verified.`)).toBeVisible();
  await expect(
    qcPage.getByRole("main").getByText("Verified", { exact: true }).first(),
  ).toBeVisible();
});
