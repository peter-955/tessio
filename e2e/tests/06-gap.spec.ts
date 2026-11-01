import { SAVED_CARD_STORY } from "../fake-jira/jira-fixtures.ts";
import {
  GAP_ANSWER,
  GAP_QUESTION,
  PROJECT_KEY,
} from "../support/constants/e2e-project.constant.ts";
import { DEV } from "../support/constants/e2e-users.constant.ts";
import { expect, test } from "../support/fixtures/role-pages.fixture.ts";
import { selectOption } from "../support/utils/select-option.util.ts";

const STORY_PATH = `/projects/${PROJECT_KEY}/stories/${SAVED_CARD_STORY.key}`;
const GAP_BANNER_TEXT = "1 open gap blocks runs";

test("the QC raises a gap that the developer must answer", async ({ qcPage }) => {
  await qcPage.goto(STORY_PATH);
  await qcPage.getByRole("tab", { name: "Gaps" }).click();
  await qcPage
    .getByRole("tabpanel", { name: "Gaps" })
    .getByRole("button", { name: "Raise gap" })
    .click();

  const dialog = qcPage.getByRole("dialog", { name: "Raise a gap" });
  await selectOption(qcPage, dialog.getByRole("combobox", { name: "Type" }), "Unclear goal");
  await expect(dialog.getByRole("radio", { name: "Story" })).toBeChecked();
  await dialog.getByRole("textbox", { name: "Question" }).fill(GAP_QUESTION);
  await selectOption(
    qcPage,
    dialog.getByRole("combobox", { name: "Assignee" }),
    new RegExp(DEV.name),
  );
  await dialog.getByRole("button", { name: "Raise gap" }).click();

  await expect(qcPage.getByText("Gap raised")).toBeVisible();
  await expect(dialog).toBeHidden();
  await expect(qcPage.getByText(GAP_BANNER_TEXT)).toBeVisible();
  await expect(
    qcPage.getByRole("tabpanel", { name: "Gaps" }).getByText(GAP_QUESTION),
  ).toBeVisible();
});

test("an open gap stops the QC from starting a run", async ({ qcPage }) => {
  await qcPage.goto(`/projects/${PROJECT_KEY}/runs/new`);
  await selectOption(
    qcPage,
    qcPage.getByRole("combobox", { name: "Story" }),
    new RegExp(SAVED_CARD_STORY.key),
  );
  await expect(qcPage.getByRole("alert", { name: GAP_BANNER_TEXT })).toBeVisible();

  await qcPage.getByRole("button", { name: "Start manual run" }).click();
  await expect(
    qcPage.getByRole("alert").filter({ hasText: "Answer the open gaps on this story first." }),
  ).toBeVisible();
  await expect(qcPage).toHaveURL(new RegExp(`/projects/${PROJECT_KEY}/runs/new$`));
});

test("the developer answers the gap and the run block is lifted", async ({ devPage, qcPage }) => {
  await devPage.goto("/gaps");
  const gapCard = devPage
    .getByRole("list", { name: "Gap questions" })
    .getByRole("listitem")
    .filter({ hasText: GAP_QUESTION });
  await gapCard.getByRole("button", { name: "Answer" }).click();
  const dialog = devPage.getByRole("dialog", { name: "Answer gap" });
  await dialog.getByRole("textbox", { name: "Your answer" }).fill(GAP_ANSWER);
  await dialog.getByRole("button", { name: "Answer and resolve" }).click();
  await expect(devPage.getByText("Gap answered")).toBeVisible();
  await expect(dialog).toBeHidden();

  await qcPage.goto(STORY_PATH);
  await qcPage.getByRole("tab", { name: "Gaps" }).click();
  await expect(qcPage.getByRole("radio", { name: "Open (0)" })).toBeChecked();
  await expect(qcPage.getByRole("radio", { name: "Answered (1)" })).toBeAttached();
  await expect(qcPage.getByText(GAP_BANNER_TEXT)).toHaveCount(0);
});
