import type {
  AdfDocument,
  JiraAccountPayload,
  JiraBoardPayload,
  JiraIssuePayload,
  JiraProjectPayload,
  JiraSprintPayload,
  JiraStoryFixture,
} from "./jira-payload.type.ts";

const DAY_MILLISECONDS = 24 * 60 * 60 * 1000;
const FIXTURE_CREATED_AT = Date.now();
const ISSUE_UPDATED_AT = new Date(FIXTURE_CREATED_AT - DAY_MILLISECONDS).toISOString();

export const JIRA_ACCOUNT: JiraAccountPayload = {
  accountId: "e2e-bot",
  displayName: "E2E Bot",
  emailAddress: "e2e-bot@example.com",
};

export const JIRA_PROJECT: JiraProjectPayload = { id: "10000", key: "SHOP", name: "Shop" };

export const JIRA_BOARD: JiraBoardPayload = { id: 1, name: "SHOP board", type: "scrum" };

export const JIRA_ACTIVE_SPRINT: JiraSprintPayload = {
  id: 11,
  name: "Sprint 1",
  state: "active",
  startDate: new Date(FIXTURE_CREATED_AT - 7 * DAY_MILLISECONDS).toISOString(),
  endDate: new Date(FIXTURE_CREATED_AT + 7 * DAY_MILLISECONDS).toISOString(),
};

export const SAVED_CARD_STORY: JiraStoryFixture = {
  key: "SHOP-1",
  summary: "Pay with a saved card",
  acceptanceCriteria: [
    "The saved card is offered at checkout",
    "Paying with the saved card places the order",
    "A declined card shows an error and keeps the basket",
  ],
};

export const ORDER_TRACKING_STORY: JiraStoryFixture = {
  key: "SHOP-2",
  summary: "Track my order",
  acceptanceCriteria: [
    "The order page shows the delivery status",
    "A shipped order shows its tracking link",
  ],
};

export const SUB_TASK_ISSUE_KEY = "SHOP-3";

const buildStoryDescription = (
  introduction: string,
  acceptanceCriteria: string[],
): AdfDocument => ({
  type: "doc",
  version: 1,
  content: [
    { type: "paragraph", content: [{ type: "text", text: introduction }] },
    {
      type: "heading",
      attrs: { level: 2 },
      content: [{ type: "text", text: "Acceptance criteria" }],
    },
    {
      type: "bulletList",
      content: acceptanceCriteria.map((criterion) => ({
        type: "listItem",
        content: [{ type: "paragraph", content: [{ type: "text", text: criterion }] }],
      })),
    },
  ],
});

export const SPRINT_ISSUES: JiraIssuePayload[] = [
  {
    id: "20001",
    key: SAVED_CARD_STORY.key,
    fields: {
      summary: SAVED_CARD_STORY.summary,
      description: buildStoryDescription(
        "As a returning shopper I want to pay with a card I saved before.",
        SAVED_CARD_STORY.acceptanceCriteria,
      ),
      status: { name: "In Progress" },
      issuetype: { name: "Story", subtask: false },
      updated: ISSUE_UPDATED_AT,
    },
  },
  {
    id: "20002",
    key: ORDER_TRACKING_STORY.key,
    fields: {
      summary: ORDER_TRACKING_STORY.summary,
      description: buildStoryDescription(
        "As a shopper I want to follow my order until it arrives.",
        ORDER_TRACKING_STORY.acceptanceCriteria,
      ),
      status: { name: "To Do" },
      issuetype: { name: "Story", subtask: false },
      updated: ISSUE_UPDATED_AT,
    },
  },
  {
    id: "20003",
    key: SUB_TASK_ISSUE_KEY,
    fields: {
      summary: "Store the card token",
      description: null,
      status: { name: "To Do" },
      issuetype: { name: "Sub-task", subtask: true },
      updated: ISSUE_UPDATED_AT,
    },
  },
];
