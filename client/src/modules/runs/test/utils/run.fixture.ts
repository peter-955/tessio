import type {
  RunCase,
  RunDetail,
  RunSummary,
  StepResult,
} from "@/shared/typing/types/test-run.type";

export const RUN_ID = "a6000000-0000-4000-8000-000000000001";

export const PARENT_RUN_ID = "a6000000-0000-4000-8000-000000000002";

export const CHILD_RUN_ID = "a6000000-0000-4000-8000-000000000003";

export const SCREENSHOT_FILE_ID = "f6000000-0000-4000-8000-000000000001";

export const EVIDENCE_FILE_ID = "f6000000-0000-4000-8000-000000000002";

export const createRunSummary = (overrides: Partial<RunSummary> = {}): RunSummary => {
  return {
    id: RUN_ID,
    storyId: "c6000000-0000-4000-8000-000000000001",
    storyJiraKey: "APP-1",
    storyTitle: "Pay by card",
    environmentId: "e6000000-0000-4000-8000-000000000001",
    environmentName: "Staging",
    executor: "claude",
    status: "failed",
    abortReason: null,
    parentRunId: null,
    startedBy: "b6000000-0000-4000-8000-000000000001",
    startedByName: "Alice Tester",
    startedAt: "2026-10-20T10:00:00Z",
    finishedAt: "2026-10-20T10:02:05Z",
    counts: { total: 6, passed: 3, failed: 1, blocked: 0, skipped: 0, notReported: 2 },
    ...overrides,
  };
};

export const createStepResult = (overrides: Partial<StepResult> = {}): StepResult => {
  return {
    order: 1,
    action: "Open the cart",
    expected: "The cart is shown",
    status: "passed",
    actualResult: "The cart was shown",
    error: null,
    screenshotFileId: null,
    screenshotStatus: null,
    evidenceFileId: null,
    ...overrides,
  };
};

export const createRunCase = (overrides: Partial<RunCase> = {}): RunCase => {
  return {
    testCaseId: "d6000000-0000-4000-8000-000000000001",
    code: "TC-1",
    title: "Pay with a valid card",
    versionId: "d6100000-0000-4000-8000-000000000001",
    versionNumber: 2,
    position: 1,
    result: {
      id: "d6200000-0000-4000-8000-000000000001",
      status: "passed",
      durationMs: 4000,
      recordedAt: "2026-10-20T10:01:00Z",
    },
    steps: [createStepResult()],
    ...overrides,
  };
};

export const createRunDetail = (overrides: Partial<RunDetail> = {}): RunDetail => {
  return {
    ...createRunSummary(),
    summary: "Checkout fails when paying by card.",
    report: null,
    childRunIds: [],
    cases: [createRunCase()],
    ...overrides,
  };
};
