import type {
  CoverageCount,
  CriterionTrace,
  LatestResult,
  Traceability,
  TracedCase,
} from "../../typing/types/traceability.type";

export const STORY_ID = "c1000000-0000-4000-8000-000000000001";

export const FIRST_CRITERION_ID = "d1000000-0000-4000-8000-000000000001";

export const SECOND_CRITERION_ID = "d1000000-0000-4000-8000-000000000002";

export const THIRD_CRITERION_ID = "d1000000-0000-4000-8000-000000000003";

export const REMOVED_CRITERION_ID = "d1000000-0000-4000-8000-000000000004";

export const FIRST_CASE_ID = "e1000000-0000-4000-8000-000000000001";

export const SECOND_CASE_ID = "e1000000-0000-4000-8000-000000000002";

export const buildLatestResult = (overrides: Partial<LatestResult> = {}): LatestResult => {
  return {
    caseResultId: "f2000000-0000-4000-8000-000000000001",
    runId: "f1000000-0000-4000-8000-000000000001",
    status: "failed",
    recordedAt: "2026-10-22T09:00:00Z",
    testCaseVersionId: "a2000000-0000-4000-8000-000000000002",
    ...overrides,
  };
};

export const buildCriterionTrace = (overrides: Partial<CriterionTrace> = {}): CriterionTrace => {
  return {
    id: FIRST_CRITERION_ID,
    code: "AC1",
    position: 1,
    text: "Card payment succeeds",
    removedAt: null,
    status: "failed",
    linkedCaseIds: [FIRST_CASE_ID],
    ...overrides,
  };
};

export const buildTracedCase = (overrides: Partial<TracedCase> = {}): TracedCase => {
  return {
    id: FIRST_CASE_ID,
    code: "TC-1",
    title: "Pay with a valid card",
    status: "ready",
    priority: "high",
    needsReview: false,
    criterionIds: [FIRST_CRITERION_ID],
    latestResult: buildLatestResult(),
    ...overrides,
  };
};

export const buildCoverageCount = (overrides: Partial<CoverageCount> = {}): CoverageCount => {
  return {
    criterionCount: 3,
    coveredCount: 2,
    passedCount: 0,
    failedCount: 1,
    blockedCount: 0,
    notRunCount: 1,
    uncoveredCount: 1,
    ...overrides,
  };
};

export const TRACED_CRITERIA: CriterionTrace[] = [
  buildCriterionTrace(),
  buildCriterionTrace({
    id: SECOND_CRITERION_ID,
    code: "AC2",
    position: 2,
    text: "Declined card shows an error",
    status: "not_run",
    linkedCaseIds: [SECOND_CASE_ID],
  }),
  buildCriterionTrace({
    id: THIRD_CRITERION_ID,
    code: "AC3",
    position: 3,
    text: "Receipt is emailed",
    status: "uncovered",
    linkedCaseIds: [],
  }),
  buildCriterionTrace({
    id: REMOVED_CRITERION_ID,
    code: "AC4",
    position: 4,
    text: "Old rule",
    removedAt: "2026-10-18T09:00:00Z",
    status: "uncovered",
    linkedCaseIds: [],
  }),
];

export const TRACED_CASES: TracedCase[] = [
  buildTracedCase(),
  buildTracedCase({
    id: SECOND_CASE_ID,
    code: "TC-2",
    title: "Decline an expired card",
    status: "draft",
    needsReview: true,
    criterionIds: [SECOND_CRITERION_ID],
    latestResult: null,
  }),
];

export const buildTraceability = (overrides: Partial<Traceability> = {}): Traceability => {
  return {
    storyId: STORY_ID,
    jiraKey: "SHOP-1",
    coverage: buildCoverageCount(),
    criteria: TRACED_CRITERIA,
    cases: TRACED_CASES,
    ...overrides,
  };
};
