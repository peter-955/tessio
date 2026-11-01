import type {
  DraftCaseItem,
  FailureToFixItem,
  GapToAnswerItem,
  MyWork,
  UncoveredCriterionItem,
} from "../../typing/types/my-work.type";

export const FAILURE_ID = "f1000000-0000-4000-8000-000000000001";

export const buildUncoveredCriterion = (
  overrides: Partial<UncoveredCriterionItem> = {},
): UncoveredCriterionItem => {
  return {
    criterionId: "a1000000-0000-4000-8000-000000000001",
    code: "AC-1",
    text: "The card is charged once",
    storyJiraKey: "SHOP-1",
    storyTitle: "Pay by card",
    ...overrides,
  };
};

export const buildDraftCase = (overrides: Partial<DraftCaseItem> = {}): DraftCaseItem => {
  return {
    caseId: "b1000000-0000-4000-8000-000000000001",
    code: "TC-7",
    title: "Refund a card payment",
    status: "draft",
    storyJiraKey: "SHOP-2",
    ...overrides,
  };
};

export const buildFailureToFix = (overrides: Partial<FailureToFixItem> = {}): FailureToFixItem => {
  return {
    failureId: FAILURE_ID,
    status: "open",
    caseCode: "TC-3",
    caseTitle: "Checkout with an expired card",
    storyJiraKey: "SHOP-3",
    openedAt: "2026-10-20T09:00:00Z",
    ...overrides,
  };
};

export const buildGapToAnswer = (overrides: Partial<GapToAnswerItem> = {}): GapToAnswerItem => {
  return {
    gapId: "d1000000-0000-4000-8000-000000000001",
    storyJiraKey: "SHOP-4",
    question: "Which currencies are allowed?",
    type: "missing_ac",
    severity: "high",
    createdAt: "2026-10-21T10:00:00Z",
    ...overrides,
  };
};

export const buildMyWork = (overrides: Partial<MyWork> = {}): MyWork => {
  return {
    role: "admin",
    sections: ["cases_to_write", "failures_to_fix", "gaps_to_answer"],
    sprint: null,
    uncoveredCriteria: { totalCount: 1, items: [buildUncoveredCriterion()] },
    draftCases: { totalCount: 1, items: [buildDraftCase()] },
    failuresToFix: { totalCount: 1, items: [buildFailureToFix()] },
    gapsToAnswer: { totalCount: 1, items: [buildGapToAnswer()] },
    unassignedFailureCount: 2,
    ...overrides,
  };
};
