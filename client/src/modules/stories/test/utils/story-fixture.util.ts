import type {
  AcceptanceCriterion,
  ProjectSyncState,
  StoryDetail,
  StorySummary,
} from "../../typing/types/story.type";

export const ACTIVE_SPRINT_ID = "5a1e2b3c-4d5e-4f60-8a1b-2c3d4e5f6a70";

export const FUTURE_SPRINT_ID = "6b2f3c4d-5e6f-4a71-9b2c-3d4e5f6a7b81";

export const buildStorySummary = (overrides: Partial<StorySummary> = {}): StorySummary => {
  return {
    id: "c1000000-0000-4000-8000-000000000001",
    jiraKey: "SHOP-1",
    jiraUrl: "https://shop.atlassian.net/browse/SHOP-1",
    title: "Pay by card",
    jiraStatus: "In Progress",
    jiraIssueType: "Story",
    source: "jira",
    testStatus: "not_started",
    sprintId: ACTIVE_SPRINT_ID,
    sprintName: "Sprint 12",
    criterionCount: 3,
    syncedAt: "2026-10-20T09:00:00Z",
    jiraMissingAt: null,
    ...overrides,
  };
};

export const buildCriterion = (
  overrides: Partial<AcceptanceCriterion> = {},
): AcceptanceCriterion => {
  return {
    id: "d1000000-0000-4000-8000-000000000001",
    code: "AC-1",
    position: 1,
    text: "Card payment succeeds",
    removedAt: null,
    isRemoved: false,
    ...overrides,
  };
};

export const buildStoryDetail = (overrides: Partial<StoryDetail> = {}): StoryDetail => {
  return {
    id: "c1000000-0000-4000-8000-000000000001",
    jiraKey: "SHOP-1",
    jiraUrl: "https://shop.atlassian.net/browse/SHOP-1",
    title: "Pay by card",
    jiraStatus: "In Progress",
    jiraIssueType: "Story",
    source: "jira",
    testStatus: "not_started",
    syncedAt: "2026-10-20T09:00:00Z",
    jiraMissingAt: null,
    description: null,
    sprint: { id: ACTIVE_SPRINT_ID, name: "Sprint 12", state: "active" },
    criteria: [buildCriterion()],
    availableTestStatuses: [],
    testStatusChangedAt: null,
    jiraUpdatedAt: "2026-10-19T09:00:00Z",
    descriptionText: null,
    ...overrides,
  };
};

export const buildSyncState = (overrides: Partial<ProjectSyncState> = {}): ProjectSyncState => {
  return {
    status: "never",
    queuedAt: null,
    startedAt: null,
    finishedAt: null,
    lastSucceededAt: null,
    errorCode: null,
    ...overrides,
  };
};
