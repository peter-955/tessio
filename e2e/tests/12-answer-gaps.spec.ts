import { ORDER_TRACKING_STORY } from "../fake-jira/jira-fixtures.ts";
import {
  CLAUDE_GAP_ANSWER,
  CLAUDE_GAP_QUESTION,
  CLAUDE_TOKEN_NAME,
  PROJECT_KEY,
} from "../support/constants/e2e-project.constant.ts";
import { DEV } from "../support/constants/e2e-users.constant.ts";
import { expect, test } from "../support/fixtures/role-pages.fixture.ts";
import type { AnsweredGapReply, MyGapsReply } from "../support/types/mcp-tool.type.ts";
import { callTessioTool, createApiToken, revokeApiToken } from "../support/utils/mcp.util.ts";
import { selectOption } from "../support/utils/select-option.util.ts";

const STORY_PATH = `/projects/${PROJECT_KEY}/stories/${ORDER_TRACKING_STORY.key}`;
const GAP_BANNER_TEXT = "1 open gap blocks runs";

test("the QC raises a gap on the order tracking story for the developer", async ({ qcPage }) => {
  await qcPage.goto(STORY_PATH);
  await qcPage.getByRole("tab", { name: "Gaps" }).click();
  await qcPage
    .getByRole("tabpanel", { name: "Gaps" })
    .getByRole("button", { name: "Raise gap" })
    .click();

  const dialog = qcPage.getByRole("dialog", { name: "Raise a gap" });
  await selectOption(qcPage, dialog.getByRole("combobox", { name: "Type" }), "Unclear goal");
  await dialog.getByRole("textbox", { name: "Question" }).fill(CLAUDE_GAP_QUESTION);
  await selectOption(
    qcPage,
    dialog.getByRole("combobox", { name: "Assignee" }),
    new RegExp(DEV.name),
  );
  await dialog.getByRole("button", { name: "Raise gap" }).click();

  await expect(qcPage.getByText("Gap raised")).toBeVisible();
  await expect(qcPage.getByText(GAP_BANNER_TEXT)).toBeVisible();
});

test("the developer answers the gap with Claude through the Tessio MCP tools", async ({
  devPage,
}) => {
  const createdToken = await createApiToken(devPage.request, PROJECT_KEY, CLAUDE_TOKEN_NAME);

  const myGaps = await callTessioTool<MyGapsReply>(
    devPage.request,
    createdToken.token,
    "get_my_gaps",
    { story_key: ORDER_TRACKING_STORY.key },
  );
  const gap = myGaps.gaps.find((listedGap) => listedGap.question === CLAUDE_GAP_QUESTION);
  if (gap === undefined) {
    throw new Error(`get_my_gaps did not list the gap: ${JSON.stringify(myGaps)}`);
  }
  expect(gap.story_key).toBe(ORDER_TRACKING_STORY.key);
  expect(gap.is_assigned_to_me).toBe(true);

  const answeredGap = await callTessioTool<AnsweredGapReply>(
    devPage.request,
    createdToken.token,
    "answer_gap",
    { gap_id: gap.id, answer: CLAUDE_GAP_ANSWER },
  );
  expect(answeredGap).toEqual({ status: "resolved", open_gap_count: 0, is_ready: true });

  const gapResponse = await devPage.request.get(`/api/projects/${PROJECT_KEY}/gaps/${gap.id}`);
  expect(gapResponse.ok()).toBe(true);
  expect(await gapResponse.json()).toMatchObject({
    status: "resolved",
    answer: CLAUDE_GAP_ANSWER,
    answeredByName: DEV.name,
    isAnsweredViaClaude: true,
  });

  await revokeApiToken(devPage.request, createdToken.apiToken.id);
});

test("the QC sees the story unblocked and the answer marked via Claude", async ({ qcPage }) => {
  await qcPage.goto(STORY_PATH);
  await qcPage.getByRole("tab", { name: "Gaps" }).click();
  const gapsPanel = qcPage.getByRole("tabpanel", { name: "Gaps" });
  await expect(gapsPanel.getByRole("radio", { name: "Open (0)" })).toBeChecked();
  await expect(qcPage.getByText(GAP_BANNER_TEXT)).toHaveCount(0);

  await gapsPanel.getByText("Answered (1)", { exact: true }).click();
  await expect(gapsPanel.getByRole("radio", { name: "Answered (1)" })).toBeChecked();
  await expect(gapsPanel.getByText(CLAUDE_GAP_ANSWER)).toBeVisible();
  await expect(gapsPanel.getByText(new RegExp(`^Answered by ${DEV.name}`))).toBeVisible();
  await expect(gapsPanel.getByText("via Claude", { exact: true })).toBeVisible();
});
