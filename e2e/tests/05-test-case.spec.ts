import { SAVED_CARD_STORY } from "../fake-jira/jira-fixtures.ts";
import { CASE, PROJECT_KEY } from "../support/constants/e2e-project.constant.ts";
import { expect, test } from "../support/fixtures/role-pages.fixture.ts";
import { mergeRunState } from "../support/utils/run-state.util.ts";
import { selectOption } from "../support/utils/select-option.util.ts";

const CASE_CODE = "TC-1";

test("the QC writes a test case and makes it ready", async ({ qcPage }) => {
  await qcPage.goto(`/projects/${PROJECT_KEY}/test-cases/new`);
  await selectOption(
    qcPage,
    qcPage.getByRole("combobox", { name: "Story" }),
    new RegExp(SAVED_CARD_STORY.key),
  );
  await qcPage.getByRole("textbox", { name: "Title" }).fill(CASE.title);
  await selectOption(qcPage, qcPage.getByRole("combobox", { name: "Priority" }), CASE.priority);
  await selectOption(
    qcPage,
    qcPage.getByRole("combobox", { name: "Covers acceptance criteria" }),
    new RegExp(`^${CASE.criterionCode}\\b`),
  );
  await qcPage.keyboard.press("Escape");

  const steps = qcPage.getByRole("region", { name: "Steps" });
  for (const [index, step] of CASE.steps.entries()) {
    if (index > 0) {
      await steps.getByRole("button", { name: "Add step" }).click();
    }
    const stepGroup = steps.getByRole("group", { name: `Step ${index + 1}`, exact: true });
    await stepGroup.getByRole("textbox", { name: "Action" }).fill(step.action);
    await stepGroup.getByRole("textbox", { name: "Expected result" }).fill(step.expectedResult);
  }

  await qcPage.getByRole("button", { name: "Create test case" }).click();
  await expect(qcPage.getByText(`${CASE_CODE} created`)).toBeVisible();
  await expect(qcPage).toHaveURL(new RegExp(`/test-cases/${CASE_CODE}$`));
  mergeRunState({ caseCode: CASE_CODE });
  await expect(
    qcPage.getByRole("heading", { name: `${CASE_CODE} · ${CASE.title}`, level: 1 }),
  ).toBeVisible();
  await expect(qcPage.getByRole("main").getByText(CASE.priority, { exact: true })).toBeVisible();
  const covers = qcPage.getByRole("region", { name: "Covers" });
  await expect(covers).toContainText(CASE.criterionCode);
  await expect(covers).toContainText(SAVED_CARD_STORY.acceptanceCriteria[0] ?? "");
  const savedSteps = qcPage.getByRole("region", { name: "Steps" }).getByRole("listitem");
  await expect(savedSteps).toHaveCount(CASE.steps.length);

  await qcPage.getByRole("button", { name: "Submit for review" }).click();
  await expect(qcPage.getByText(`${CASE_CODE} is now In review`)).toBeVisible();
  await qcPage.getByRole("button", { name: "Mark ready" }).click();
  await expect(qcPage.getByText(`${CASE_CODE} is now Ready`)).toBeVisible();
});

test("the developer marks the story ready for test", async ({ devPage }) => {
  await devPage.goto(`/projects/${PROJECT_KEY}/stories/${SAVED_CARD_STORY.key}`);
  await devPage.getByRole("button", { name: "Mark ready for test" }).click();
  await expect(devPage.getByText("Test status is now Ready for test.")).toBeVisible();
});
