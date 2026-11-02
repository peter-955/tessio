import type { SuiteCase, SuiteDetail, SuiteSummary } from "../../typing/types/suite.type";

export const SUITE_ID = "5a000000-0000-4000-8000-000000000001";

export const ARCHIVED_SUITE_ID = "5a000000-0000-4000-8000-000000000002";

export const RUN_ID = "5b000000-0000-4000-8000-000000000001";

export const CREATOR_ID = "5c000000-0000-4000-8000-000000000001";

export const CASE_IDS = [
  "5d000000-0000-4000-8000-000000000001",
  "5d000000-0000-4000-8000-000000000002",
  "5d000000-0000-4000-8000-000000000003",
] as const;

export const buildSuiteSummary = (overrides: Partial<SuiteSummary> = {}): SuiteSummary => {
  return {
    id: SUITE_ID,
    name: "Checkout regression",
    description: "Everything a buyer does at the till.",
    caseCount: 3,
    readyCaseCount: 2,
    archivedAt: null,
    createdAt: "2026-10-20T09:00:00Z",
    lastRun: null,
    ...overrides,
  };
};

export const buildSuiteCase = (overrides: Partial<SuiteCase> = {}): SuiteCase => {
  return {
    testCaseId: CASE_IDS[0],
    code: "TC-1",
    title: "Pay with a valid card",
    status: "ready",
    priority: "high",
    isNeedingReview: false,
    isRunnable: true,
    storyId: "5e000000-0000-4000-8000-000000000001",
    storyJiraKey: "SHOP-1",
    storyTitle: "Pay by card",
    position: 0,
    ...overrides,
  };
};

export const SUITE_CASES: SuiteCase[] = [
  buildSuiteCase(),
  buildSuiteCase({
    testCaseId: CASE_IDS[1],
    code: "TC-2",
    title: "Refund an order",
    storyId: "5e000000-0000-4000-8000-000000000002",
    storyJiraKey: "SHOP-2",
    storyTitle: "Refunds",
    position: 1,
  }),
  buildSuiteCase({
    testCaseId: CASE_IDS[2],
    code: "TC-3",
    title: "Pay with a voucher",
    status: "draft",
    priority: "low",
    isRunnable: false,
    position: 2,
  }),
];

export const buildSuiteDetail = (overrides: Partial<SuiteDetail> = {}): SuiteDetail => {
  return {
    id: SUITE_ID,
    name: "Checkout regression",
    description: "Everything a buyer does at the till.",
    archivedAt: null,
    createdBy: CREATOR_ID,
    createdAt: "2026-10-20T09:00:00Z",
    caseCount: SUITE_CASES.length,
    readyCaseCount: 2,
    cases: SUITE_CASES,
    lastRun: null,
    runningRun: null,
    ...overrides,
  };
};

export const reorderSuiteCases = (caseIds: readonly string[]): SuiteCase[] => {
  return caseIds.map((caseId, position) => {
    const suiteCase = SUITE_CASES.find((candidate) => {
      return candidate.testCaseId === caseId;
    });
    if (suiteCase === undefined) {
      throw new Error(`Unknown case ${caseId}`);
    }

    return { ...suiteCase, position };
  });
};
