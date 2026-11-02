import {
  VIEWER_CAPABILITIES,
  buildProject,
} from "@/components/project-context/test/utils/project-fixture.util";
import type {
  Project,
  ProjectCapability,
} from "@/components/project-context/typing/types/project.type";
import type {
  ManualRun,
  ManualRunCase,
  ManualRunCreated,
  ManualRunStep,
  ReadyTestCase,
  RunEnvironment,
  RunStory,
} from "../../typing/types/manual-run.type";

export const CURRENT_USER_ID = "a1000000-0000-4000-8000-000000000001";

export const OTHER_USER_ID = "a1000000-0000-4000-8000-000000000002";

export const RUN_ID = "d1000000-0000-4000-8000-000000000001";

export const NEW_RUN_ID = "d1000000-0000-4000-8000-000000000002";

export const STORY_ID = "c1000000-0000-4000-8000-000000000001";

export const FIRST_CASE_ID = "e1000000-0000-4000-8000-000000000001";

export const SECOND_CASE_ID = "e1000000-0000-4000-8000-000000000002";

export const THIRD_CASE_ID = "e1000000-0000-4000-8000-000000000003";

export const STAGING_ID = "b1000000-0000-4000-8000-000000000001";

export const PRODUCTION_ID = "b1000000-0000-4000-8000-000000000002";

export const QC_CAPABILITIES: ProjectCapability[] = [
  ...VIEWER_CAPABILITIES,
  "test_case.edit",
  "run.start",
  "run.record_manual",
  "secret.use_in_run",
];

export const ADMIN_CAPABILITIES: ProjectCapability[] = [...QC_CAPABILITIES, "run.finish_any"];

export const buildRunProject = (overrides: Partial<Project> = {}): Project => {
  return buildProject({
    myRole: "qc",
    capabilities: QC_CAPABILITIES,
    allowedFileTypes: ["text/plain"],
    ...overrides,
  });
};

export const buildStep = (overrides: Partial<ManualRunStep> = {}): ManualRunStep => {
  return {
    order: 1,
    action: "Open the cart",
    expected: "The cart opens",
    status: null,
    actualResult: null,
    error: null,
    screenshotFileId: null,
    screenshotStatus: null,
    evidenceFileId: null,
    diagnosis: null,
    ...overrides,
  };
};

export const buildRunCase = (overrides: Partial<ManualRunCase> = {}): ManualRunCase => {
  return {
    testCaseId: FIRST_CASE_ID,
    code: "TC-1",
    title: "Pay by card",
    versionId: "f2000000-0000-4000-8000-000000000001",
    versionNumber: 1,
    position: 1,
    businessValue: null,
    preconditions: null,
    criteria: [],
    files: [],
    result: null,
    parameters: [],
    iterations: [],
    steps: [
      buildStep({ order: 1, action: "Open the cart", expected: "The cart opens" }),
      buildStep({ order: 2, action: "Pay by card", expected: "The order is paid" }),
    ],
    ...overrides,
  };
};

export const buildRun = (overrides: Partial<ManualRun> = {}): ManualRun => {
  return {
    id: RUN_ID,
    storyId: STORY_ID,
    storyJiraKey: "SHOP-1",
    storyTitle: "Checkout",
    environmentId: STAGING_ID,
    environmentName: "Staging",
    executor: "manual",
    status: "running",
    abortReason: null,
    parentRunId: null,
    startedBy: CURRENT_USER_ID,
    startedByName: "Quinn QC",
    startedAt: "2026-10-01T09:00:00Z",
    finishedAt: null,
    counts: { total: 2, passed: 0, failed: 0, blocked: 0, skipped: 0, notReported: 2 },
    summary: null,
    report: null,
    childRunIds: [],
    environmentBaseUrl: "https://staging.shop.test",
    data: [],
    cases: [
      buildRunCase(),
      buildRunCase({
        testCaseId: SECOND_CASE_ID,
        code: "TC-2",
        title: "Pay by voucher",
        position: 2,
        steps: [buildStep({ order: 1, action: "Apply a voucher", expected: null })],
      }),
    ],
    ...overrides,
  };
};

export const buildRecordedResult = (
  status: NonNullable<ManualRunCase["result"]>["status"],
): NonNullable<ManualRunCase["result"]> => {
  return {
    id: "f3000000-0000-4000-8000-000000000001",
    status,
    durationMs: null,
    suspectedCause: null,
    causeReason: null,
    recordedAt: "2026-10-01T09:10:00Z",
    iteration: 0,
  };
};

export const buildCreatedRun = (overrides: Partial<ManualRunCreated> = {}): ManualRunCreated => {
  return {
    id: NEW_RUN_ID,
    storyId: STORY_ID,
    environmentId: STAGING_ID,
    executor: "manual",
    status: "running",
    parentRunId: null,
    startedBy: CURRENT_USER_ID,
    startedAt: "2026-10-01T09:00:00Z",
    finishedAt: null,
    abortReason: null,
    summary: null,
    cases: [],
    ...overrides,
  };
};

export const buildStory = (overrides: Partial<RunStory> = {}): RunStory => {
  return {
    id: STORY_ID,
    jiraKey: "SHOP-1",
    jiraUrl: "https://jira.example.test/browse/SHOP-1",
    title: "Checkout",
    jiraStatus: "In Progress",
    jiraIssueType: "Story",
    source: "jira",
    testStatus: "in_test",
    sprintId: null,
    sprintName: null,
    criterionCount: 2,
    syncedAt: "2026-10-01T09:00:00Z",
    jiraMissingAt: null,
    ...overrides,
  };
};

export const buildReadyTestCase = (overrides: Partial<ReadyTestCase> = {}): ReadyTestCase => {
  return {
    id: FIRST_CASE_ID,
    code: "TC-1",
    storyId: STORY_ID,
    storyKey: "SHOP-1",
    title: "Pay by card",
    priority: "high",
    status: "ready",
    currentVersionId: "f2000000-0000-4000-8000-000000000001",
    currentVersionNumber: 1,
    stepCount: 2,
    criterionIds: [],
    needsReview: false,
    needsReviewAt: null,
    lastSavedAt: "2026-10-01T09:00:00Z",
    labels: [],
    isFlaky: false,
    flakyScore: 0,
    isDisagreeing: false,
    isQuarantined: false,
    quarantinedAt: null,
    ...overrides,
  };
};

export const buildEnvironment = (overrides: Partial<RunEnvironment> = {}): RunEnvironment => {
  return {
    id: STAGING_ID,
    name: "Staging",
    baseUrl: "https://staging.example.test",
    healthCheckUrl: null,
    isArchived: false,
    archivedAt: null,
    createdAt: "2026-10-01T09:00:00Z",
    ...overrides,
  };
};
