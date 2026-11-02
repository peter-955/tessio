import type { ProjectMember } from "@/components/project-context/typing/types/project.type";
import type { StorySummary } from "@/modules/stories/typing/types/story.type";
import type { Failure, FailureDetail, FailureRun } from "../../typing/types/failure.type";

export const CURRENT_USER_ID = "a1000000-0000-4000-8000-000000000001";

export const ASSIGNEE_ID = "a1000000-0000-4000-8000-000000000002";

export const DEACTIVATED_USER_ID = "a1000000-0000-4000-8000-000000000003";

export const INVITED_USER_ID = "a1000000-0000-4000-8000-000000000004";

export const FAILURE_ID = "f1000000-0000-4000-8000-000000000001";

export const TEST_CASE_ID = "e1000000-0000-4000-8000-000000000001";

export const CASE_RESULT_ID = "d1000000-0000-4000-8000-000000000001";

export const RUN_ID = "b1000000-0000-4000-8000-000000000001";

export const SCREENSHOT_FILE_ID = "c1000000-0000-4000-8000-0000000000aa";

export const STORY_ID = "c1000000-0000-4000-8000-000000000001";

export const buildFailure = (overrides: Partial<Failure> = {}): Failure => {
  return {
    id: FAILURE_ID,
    projectKey: "SHOP",
    storyId: STORY_ID,
    storyJiraKey: "SHOP-1",
    storyTitle: "Pay by card",
    testCaseId: TEST_CASE_ID,
    testCaseCode: "TC-1",
    testCaseTitle: "Pay with a valid card",
    status: "open",
    isActive: true,
    assigneeId: null,
    assigneeName: null,
    assigneeStatus: null,
    openedByCaseResultId: CASE_RESULT_ID,
    latestCaseResultId: CASE_RESULT_ID,
    latestRunId: RUN_ID,
    latestFailedAt: "2026-10-21T10:30:00Z",
    statusChangedAt: null,
    statusChangedByName: null,
    cause: null,
    causeReason: null,
    causeChangedAt: null,
    createdAt: "2026-10-20T09:00:00Z",
    ...overrides,
  };
};

export const buildFailureDetail = (overrides: Partial<FailureDetail> = {}): FailureDetail => {
  return {
    ...buildFailure(),
    failedStep: {
      stepOrder: 2,
      actualResult: "The pay button stayed disabled",
      error: "TimeoutError: button not enabled",
      screenshotFileId: SCREENSHOT_FILE_ID,
      diagnosis: null,
    },
    results: [
      {
        caseResultId: CASE_RESULT_ID,
        runId: RUN_ID,
        runStatus: "failed",
        runExecutor: "claude",
        status: "failed",
        durationMs: 65000,
        recordedAt: "2026-10-21T10:30:00Z",
        startedByName: "Quinn Qc",
        iteration: null,
      },
    ],
    events: [
      {
        id: "e2000000-0000-4000-8000-000000000001",
        kind: "opened",
        fromStatus: null,
        toStatus: "open",
        fromCause: null,
        toCause: null,
        caseResultId: CASE_RESULT_ID,
        runId: RUN_ID,
        assigneeId: null,
        assigneeName: null,
        actorId: null,
        actorName: null,
        createdAt: "2026-10-20T09:00:00Z",
      },
      {
        id: "e2000000-0000-4000-8000-000000000002",
        kind: "assigned",
        fromStatus: null,
        toStatus: null,
        fromCause: null,
        toCause: null,
        caseResultId: null,
        runId: null,
        assigneeId: ASSIGNEE_ID,
        assigneeName: "Dev Dana",
        actorId: CURRENT_USER_ID,
        actorName: "Quinn Qc",
        createdAt: "2026-10-20T10:00:00Z",
      },
    ],
    ...overrides,
  };
};

export const buildFailureRun = (
  screenshotStatus: "pending" | "uploaded" | "missing" = "uploaded",
  overrides: Partial<FailureRun> = {},
): FailureRun => {
  return {
    id: RUN_ID,
    storyId: STORY_ID,
    storyJiraKey: "SHOP-1",
    storyTitle: "Pay by card",
    environmentId: "a2000000-0000-4000-8000-000000000001",
    environmentName: "Staging",
    executor: "claude",
    status: "failed",
    abortReason: null,
    parentRunId: null,
    startedBy: CURRENT_USER_ID,
    startedByName: "Quinn Qc",
    startedAt: "2026-10-21T10:28:00Z",
    finishedAt: "2026-10-21T10:31:00Z",
    counts: { total: 1, passed: 0, failed: 1, blocked: 0, skipped: 0, notReported: 0 },
    summary: null,
    report: null,
    childRunIds: [],
    environmentBaseUrl: "https://staging.shop.test",
    data: [],
    cases: [
      {
        testCaseId: TEST_CASE_ID,
        code: "TC-1",
        title: "Pay with a valid card",
        versionId: "a3000000-0000-4000-8000-000000000001",
        versionNumber: 1,
        position: 1,
        businessValue: null,
        preconditions: null,
        criteria: [],
        files: [],
        result: {
          id: CASE_RESULT_ID,
          status: "failed",
          durationMs: 65000,
          suspectedCause: null,
          causeReason: null,
          recordedAt: "2026-10-21T10:30:00Z",
          iteration: 0,
        },
        parameters: [],
        iterations: [],
        steps: [
          {
            order: 1,
            action: "Open the checkout",
            expected: "The checkout shows",
            status: "passed",
            actualResult: "Shown",
            error: null,
            screenshotFileId: null,
            screenshotStatus: null,
            evidenceFileId: null,
            diagnosis: null,
          },
          {
            order: 2,
            action: "Click Pay with a valid card",
            expected: "The order is confirmed",
            status: "failed",
            actualResult: "The pay button stayed disabled",
            error: "TimeoutError: button not enabled",
            screenshotFileId: SCREENSHOT_FILE_ID,
            screenshotStatus,
            evidenceFileId: null,
            diagnosis: null,
          },
        ],
      },
    ],
    ...overrides,
  };
};

export const buildMember = (overrides: Partial<ProjectMember> = {}): ProjectMember => {
  return {
    userId: ASSIGNEE_ID,
    name: "Dev Dana",
    email: "dana.dev@example.test",
    userStatus: "active",
    role: "dev",
    addedAt: "2026-10-01T09:00:00Z",
    ...overrides,
  };
};

export const MEMBERS: ProjectMember[] = [
  buildMember(),
  buildMember({
    userId: CURRENT_USER_ID,
    name: "Quinn Qc",
    email: "quinn@example.test",
    role: "qc",
  }),
  buildMember({
    userId: DEACTIVATED_USER_ID,
    name: "Ann Old",
    email: "ann@example.test",
    role: "ba",
    userStatus: "deactivated",
  }),
  buildMember({
    userId: INVITED_USER_ID,
    name: "Ivy New",
    email: "ivy@example.test",
    role: "viewer",
    userStatus: "invited",
  }),
];

export const buildStorySummary = (overrides: Partial<StorySummary> = {}): StorySummary => {
  return {
    id: STORY_ID,
    jiraKey: "SHOP-1",
    jiraUrl: "https://shop.atlassian.net/browse/SHOP-1",
    title: "Pay by card",
    jiraStatus: "In Progress",
    jiraIssueType: "Story",
    source: "jira",
    testStatus: "not_started",
    sprintId: null,
    sprintName: null,
    criterionCount: 3,
    syncedAt: "2026-10-20T09:00:00Z",
    jiraMissingAt: null,
    ...overrides,
  };
};
