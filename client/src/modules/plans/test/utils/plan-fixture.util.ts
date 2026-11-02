import type { StorySummary } from "@/modules/stories/typing/types/story.type";
import type {
  PlanCase,
  PlanDetail,
  PlanFailure,
  PlanGap,
  PlanItem,
  PlanProgressCounts,
  PlanSuiteSummary,
  PlanSummary,
} from "../../typing/types/plan.type";

export const PLAN_ID = "0b9f7a52-3c1e-4c55-9a8e-6d3f2a1b4c01";

export const SUITE_ID = "1c2d3e4f-5a6b-4c7d-8e9f-0a1b2c3d4e01";

export const OTHER_SUITE_ID = "1c2d3e4f-5a6b-4c7d-8e9f-0a1b2c3d4e02";

export const STORY_ID = "2d3e4f5a-6b7c-4d8e-9f0a-1b2c3d4e5f01";

export const ENVIRONMENT_ID = "3e4f5a6b-7c8d-4e9f-8a1b-2c3d4e5f6a01";

export const USER_ID = "4f5a6b7c-8d9e-4f0a-9b2c-3d4e5f6a7b01";

export const RUN_ID = "5a6b7c8d-9e0f-4a1b-8c3d-4e5f6a7b8c01";

export const FAILURE_ID = "6b7c8d9e-0f1a-4b2c-9d4e-5f6a7b8c9d01";

export const buildCounts = (overrides: Partial<PlanProgressCounts> = {}): PlanProgressCounts => {
  return { total: 0, passed: 0, failed: 0, blocked: 0, skipped: 0, notRun: 0, ...overrides };
};

export const buildPlanSummary = (overrides: Partial<PlanSummary> = {}): PlanSummary => {
  return {
    id: PLAN_ID,
    name: "Release 4.2",
    description: "Everything for the 4.2 release",
    status: "open",
    targetDate: "2026-11-20",
    environmentId: ENVIRONMENT_ID,
    environmentName: "Staging",
    itemCount: 2,
    counts: buildCounts({ total: 4, passed: 2, failed: 1, notRun: 1 }),
    createdBy: USER_ID,
    createdAt: "2026-11-01T09:00:00Z",
    signedOffAt: null,
    closedAt: null,
    ...overrides,
  };
};

export const buildPlanCase = (overrides: Partial<PlanCase> = {}): PlanCase => {
  return {
    testCaseId: "7c8d9e0f-1a2b-4c3d-8e5f-6a7b8c9d0e01",
    code: "TC-1",
    title: "Pay with a valid card",
    status: "ready",
    priority: "high",
    isNeedingReview: false,
    storyId: STORY_ID,
    storyJiraKey: "SHOP-12",
    storyTitle: "Checkout",
    latestResult: {
      caseResultId: "8d9e0f1a-2b3c-4d4e-9f6a-7b8c9d0e1f01",
      runId: RUN_ID,
      status: "passed",
      recordedAt: "2026-11-02T10:00:00Z",
    },
    activeFailureId: null,
    activeFailureStatus: null,
    ...overrides,
  };
};

export const PLAN_CASES: PlanCase[] = [
  buildPlanCase(),
  buildPlanCase({
    testCaseId: "7c8d9e0f-1a2b-4c3d-8e5f-6a7b8c9d0e02",
    code: "TC-2",
    title: "Refuse an expired card",
    latestResult: {
      caseResultId: "8d9e0f1a-2b3c-4d4e-9f6a-7b8c9d0e1f02",
      runId: RUN_ID,
      status: "failed",
      recordedAt: "2026-11-02T10:05:00Z",
    },
    activeFailureId: FAILURE_ID,
    activeFailureStatus: "open",
  }),
  buildPlanCase({
    testCaseId: "7c8d9e0f-1a2b-4c3d-8e5f-6a7b8c9d0e03",
    code: "TC-3",
    title: "Pay with a gift card",
    status: "draft",
    isNeedingReview: true,
    latestResult: null,
  }),
];

export const PLAN_FAILURE: PlanFailure = {
  failureId: FAILURE_ID,
  testCaseId: "7c8d9e0f-1a2b-4c3d-8e5f-6a7b8c9d0e02",
  code: "TC-2",
  title: "Refuse an expired card",
  storyJiraKey: "SHOP-12",
  status: "open",
  assigneeId: null,
  assigneeName: null,
  createdAt: "2026-11-02T10:05:00Z",
};

export const PLAN_GAP: PlanGap = {
  gapId: "9e0f1a2b-3c4d-4e5f-8a7b-8c9d0e1f2a01",
  storyId: STORY_ID,
  storyJiraKey: "SHOP-12",
  question: "Which card brands are accepted?",
  severity: "high",
  assigneeId: null,
  assigneeName: null,
  assigneeRole: "ba",
  createdAt: "2026-11-01T11:00:00Z",
};

export const PLAN_ITEMS: PlanItem[] = [
  {
    position: 0,
    kind: "suite",
    suiteId: SUITE_ID,
    storyId: null,
    name: "Checkout regression",
    storyJiraKey: null,
    archivedAt: null,
    caseCount: 2,
  },
  {
    position: 1,
    kind: "story",
    suiteId: null,
    storyId: STORY_ID,
    name: "Checkout",
    storyJiraKey: "SHOP-12",
    archivedAt: null,
    caseCount: 3,
  },
];

export const buildPlanDetail = (overrides: Partial<PlanDetail> = {}): PlanDetail => {
  return {
    id: PLAN_ID,
    name: "Release 4.2",
    description: "Everything for the 4.2 release",
    status: "open",
    targetDate: "2026-11-20",
    environmentId: ENVIRONMENT_ID,
    environmentName: "Staging",
    createdBy: USER_ID,
    createdByName: "Quinn Qc",
    createdAt: "2026-11-01T09:00:00Z",
    signedOffBy: null,
    signedOffByName: null,
    signedOffAt: null,
    closedBy: null,
    closedByName: null,
    closedAt: null,
    items: PLAN_ITEMS,
    progress: {
      counts: buildCounts({ total: 3, passed: 1, failed: 1, notRun: 1 }),
      cases: PLAN_CASES,
      failures: [PLAN_FAILURE],
      gaps: [PLAN_GAP],
    },
    ...overrides,
  };
};

export const buildPassingPlanDetail = (overrides: Partial<PlanDetail> = {}): PlanDetail => {
  return buildPlanDetail({
    progress: {
      counts: buildCounts({ total: 1, passed: 1 }),
      cases: [buildPlanCase()],
      failures: [],
      gaps: [],
    },
    ...overrides,
  });
};

export const PLAN_SUITES: PlanSuiteSummary[] = [
  {
    id: SUITE_ID,
    name: "Checkout regression",
    description: null,
    caseCount: 2,
    readyCaseCount: 2,
    archivedAt: null,
    createdAt: "2026-10-20T09:00:00Z",
    lastRun: null,
  },
  {
    id: OTHER_SUITE_ID,
    name: "Search regression",
    description: null,
    caseCount: 5,
    readyCaseCount: 4,
    archivedAt: null,
    createdAt: "2026-10-21T09:00:00Z",
    lastRun: null,
  },
];

export const OTHER_STORY_ID = "2d3e4f5a-6b7c-4d8e-9f0a-1b2c3d4e5f02";

export const PLAN_STORIES: StorySummary[] = [
  {
    id: STORY_ID,
    jiraKey: "SHOP-12",
    jiraUrl: "https://shop.atlassian.net/browse/SHOP-12",
    title: "Checkout",
    jiraStatus: "In Progress",
    jiraIssueType: "Story",
    testStatus: "in_test",
    sprintId: null,
    sprintName: null,
    criterionCount: 3,
    syncedAt: "2026-11-01T08:00:00Z",
    jiraMissingAt: null,
    source: "jira",
  },
  {
    id: OTHER_STORY_ID,
    jiraKey: "SHOP-13",
    jiraUrl: "https://shop.atlassian.net/browse/SHOP-13",
    title: "Wish list",
    jiraStatus: "In Progress",
    jiraIssueType: "Story",
    testStatus: "not_started",
    sprintId: null,
    sprintName: null,
    criterionCount: 2,
    syncedAt: "2026-11-01T08:00:00Z",
    jiraMissingAt: null,
    source: "jira",
  },
];
