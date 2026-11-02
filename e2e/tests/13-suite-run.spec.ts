import { SAVED_CARD_STORY } from "../fake-jira/jira-fixtures.ts";
import {
  CASE,
  ENVIRONMENT,
  PLAN_NAME,
  PROJECT_KEY,
  REGRESSION_LABEL,
  SUITE_GAP_ANSWER,
  SUITE_GAP_QUESTION,
  SUITE_NAME,
} from "../support/constants/e2e-project.constant.ts";
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
import { expectStoryTestStatus } from "../support/utils/story-status.util.ts";

const STORY_PATH = `/projects/${PROJECT_KEY}/stories/${SAVED_CARD_STORY.key}`;
const SUITE_PATH_PATTERN = new RegExp(`/projects/${PROJECT_KEY}/suites/([^/?]+)$`);
const OPEN_GAPS_MESSAGE =
  "Open gaps on this suite's stories must be answered before it can run. Answer them on the stories, or with /tessio:answer-gaps in Claude Code.";

const suitePath = (): string => `/projects/${PROJECT_KEY}/suites/${requireRunValue("suiteId")}`;

const suiteCaseName = (caseCode: string): RegExp =>
  new RegExp(`^${caseCode} · ${CASE.title} · ${SAVED_CARD_STORY.key}`);

test("the QC labels the saved card case for regression", async ({ qcPage }) => {
  const caseCode = requireRunValue("caseCode");
  await qcPage.goto(`/projects/${PROJECT_KEY}/test-cases/${caseCode}`);
  await qcPage.getByRole("button", { name: "Edit labels" }).click();
  await qcPage.getByRole("textbox", { name: "New label" }).fill(REGRESSION_LABEL);
  await qcPage.getByRole("button", { name: "Create and add" }).click();
  await expect(qcPage.getByRole("textbox", { name: "New label" })).toHaveValue("");
  await qcPage.getByRole("button", { name: "Save labels" }).click();
  await expect(qcPage.getByText("Labels saved")).toBeVisible();
  await expect(
    qcPage.getByRole("list", { name: "Labels" }).getByText(REGRESSION_LABEL, { exact: true }),
  ).toBeVisible();
});

test("the QC creates a suite and adds the regression cases by label", async ({ qcPage }) => {
  const caseCode = requireRunValue("caseCode");
  await qcPage.goto(`/projects/${PROJECT_KEY}/suites`);
  await qcPage.getByRole("button", { name: "New suite" }).first().click();
  const createDialog = qcPage.getByRole("dialog", { name: "New suite" });
  await createDialog.getByRole("textbox", { name: /^Name/ }).fill(SUITE_NAME);
  await createDialog.getByRole("button", { name: "Create suite" }).click();
  await expect(qcPage.getByText("Suite created")).toBeVisible();

  await expect(qcPage).toHaveURL(SUITE_PATH_PATTERN);
  const suiteId = SUITE_PATH_PATTERN.exec(new URL(qcPage.url()).pathname)?.[1];
  expect(suiteId).toBeDefined();
  mergeRunState({ suiteId: suiteId ?? "" });
  await expect(qcPage.getByRole("heading", { name: SUITE_NAME, level: 1 })).toBeVisible();

  await qcPage.getByRole("button", { name: "Add by filter" }).first().click();
  const filterDialog = qcPage.getByRole("dialog", { name: "Add cases by filter" });
  await selectOption(
    qcPage,
    filterDialog.getByRole("combobox", { name: "Labels" }),
    REGRESSION_LABEL,
  );
  await qcPage.keyboard.press("Escape");
  await filterDialog.getByRole("button", { name: "Add matching cases" }).click();
  await expect(qcPage.getByText("1 case added")).toBeVisible();

  const suiteCases = qcPage.getByRole("list", { name: "Cases of the suite" });
  await expect(suiteCases.getByRole("listitem")).toHaveCount(1);
  await expect(suiteCases).toContainText(caseCode);
  await expect(qcPage.getByText("1 case · 1 ready to run")).toBeVisible();
  await expect(qcPage.getByText(`/tessio:run-suite "${SUITE_NAME}"`)).toBeVisible();
});

test("the QC raises a gap on the saved card story for the developer", async ({ qcPage }) => {
  await qcPage.goto(STORY_PATH);
  await qcPage.getByRole("tab", { name: "Gaps" }).click();
  await qcPage
    .getByRole("tabpanel", { name: "Gaps" })
    .getByRole("button", { name: "Raise gap" })
    .click();

  const dialog = qcPage.getByRole("dialog", { name: "Raise a gap" });
  await selectOption(qcPage, dialog.getByRole("combobox", { name: "Type" }), "Unclear goal");
  await dialog.getByRole("textbox", { name: "Question" }).fill(SUITE_GAP_QUESTION);
  await selectOption(
    qcPage,
    dialog.getByRole("combobox", { name: "Assignee" }),
    new RegExp(DEV.name),
  );
  await dialog.getByRole("button", { name: "Raise gap" }).click();
  await expect(qcPage.getByText("Gap raised")).toBeVisible();
});

test("the open gap blocks a manual run of the suite", async ({ qcPage }) => {
  const caseCode = requireRunValue("caseCode");
  await qcPage.goto(suitePath());
  await qcPage.getByRole("link", { name: "Start manual run" }).click();

  await expect(qcPage).toHaveURL(/\/runs\/new\?suite=/);
  await expect(qcPage.getByRole("radio", { name: "A suite" })).toBeChecked();
  await expect(qcPage.getByRole("combobox", { name: "Environment" })).toHaveValue(ENVIRONMENT.name);
  await expect(qcPage.getByRole("checkbox", { name: suiteCaseName(caseCode) })).toBeChecked();

  await qcPage.getByRole("button", { name: "Start manual run" }).click();
  await expect(qcPage.getByText(OPEN_GAPS_MESSAGE)).toBeVisible();
  await expect(qcPage).toHaveURL(/\/runs\/new\?suite=/);
});

test("the developer answers the gap", async ({ devPage }) => {
  await devPage.goto("/gaps");
  const gapCard = devPage
    .getByRole("list", { name: "Gap questions" })
    .getByRole("listitem")
    .filter({ hasText: SUITE_GAP_QUESTION });
  await gapCard.getByRole("button", { name: "Answer" }).click();
  const dialog = devPage.getByRole("dialog", { name: "Answer gap" });
  await dialog.getByRole("textbox", { name: "Your answer" }).fill(SUITE_GAP_ANSWER);
  await dialog.getByRole("button", { name: "Answer and resolve" }).click();
  await expect(devPage.getByText("Gap answered")).toBeVisible();
});

test("the QC opens a test plan that covers the suite", async ({ qcPage }) => {
  const caseCode = requireRunValue("caseCode");
  await qcPage.goto(`/projects/${PROJECT_KEY}/plans`);
  await qcPage.getByRole("button", { name: "New plan" }).first().click();
  const createDialog = qcPage.getByRole("dialog", { name: "New test plan" });
  await createDialog.getByRole("textbox", { name: /^Name/ }).fill(PLAN_NAME);
  await createDialog.getByRole("button", { name: "Create plan" }).click();
  await expect(qcPage.getByText("Plan created.")).toBeVisible();
  await expect(qcPage.getByRole("heading", { name: PLAN_NAME, level: 1 })).toBeVisible();

  await qcPage.getByRole("button", { name: "Choose suites and stories" }).click();
  const itemsDialog = qcPage.getByRole("dialog", { name: "Choose suites and stories" });
  await selectOption(
    qcPage,
    itemsDialog.getByRole("combobox", { name: "Regression suites" }),
    SUITE_NAME,
  );
  await qcPage.keyboard.press("Escape");
  await itemsDialog.getByRole("button", { name: "Save" }).click();
  await expect(qcPage.getByText("The plan's suites and stories were saved.")).toBeVisible();

  await expect(qcPage.getByRole("link", { name: SUITE_NAME })).toBeVisible();
  await expect(
    qcPage
      .getByRole("region", { name: "Plan cases" })
      .getByRole("row", { name: new RegExp(caseCode) }),
  ).toBeVisible();
  await expect(qcPage.getByText("0 of 1 cases passed")).toBeVisible();
});

test("the QC runs the suite manually and the results are grouped by story", async ({ qcPage }) => {
  const caseCode = requireRunValue("caseCode");
  await qcPage.goto(suitePath());
  await qcPage.getByRole("link", { name: "Start manual run" }).click();
  await expect(qcPage.getByRole("checkbox", { name: suiteCaseName(caseCode) })).toBeChecked();
  await qcPage.getByRole("button", { name: "Start manual run" }).click();

  await expect(qcPage).toHaveURL(/\/record$/);
  const suiteRunId = readRunIdFromRecordUrl(qcPage);
  mergeRunState({ suiteRunId });
  await expect(
    qcPage.getByRole("heading", { name: `Manual run · ${SUITE_NAME}`, level: 1 }),
  ).toBeVisible();
  await recordStep(qcPage, 1, "Passed");
  await recordStep(qcPage, 2, "Passed");
  await saveCaseResult(qcPage, caseCode);
  await expect(qcPage.getByText(/1 of 1 cases recorded/)).toBeVisible();
  await finishRun(qcPage);

  await qcPage.goto(`/projects/${PROJECT_KEY}/runs/${suiteRunId}`);
  await expect(
    qcPage.getByRole("heading", { name: `Suite run · ${SUITE_NAME}`, level: 1 }),
  ).toBeVisible();
  await expectRunStatus(qcPage, "Passed");
  await expect(
    qcPage
      .getByRole("heading", {
        name: `${SAVED_CARD_STORY.key} · ${SAVED_CARD_STORY.summary}`,
        level: 3,
      })
      .first(),
  ).toBeVisible();

  await qcPage.goto(STORY_PATH);
  await expectStoryTestStatus(qcPage, "Passed");
});

test("the QC signs off the plan once its case has passed", async ({ qcPage }) => {
  await qcPage.goto(`/projects/${PROJECT_KEY}/plans`);
  await qcPage.getByRole("link", { name: PLAN_NAME }).click();
  await expect(qcPage.getByRole("heading", { name: PLAN_NAME, level: 1 })).toBeVisible();
  await expect(qcPage.getByText("1 of 1 cases passed")).toBeVisible();
  await expect(qcPage.getByText("No active failure on this plan's cases.")).toBeVisible();

  await qcPage.getByRole("button", { name: "Sign off" }).click();
  const dialog = qcPage.getByRole("dialog", { name: `Sign off ${PLAN_NAME}?` });
  await dialog.getByRole("button", { name: "Sign off" }).click();
  await expect(qcPage.getByText("Plan signed off.")).toBeVisible();
  await expect(
    qcPage.getByRole("main").getByText("Signed off", { exact: true }).first(),
  ).toBeVisible();
  await expect(qcPage.getByRole("button", { name: "Sign off" })).toHaveCount(0);
});
