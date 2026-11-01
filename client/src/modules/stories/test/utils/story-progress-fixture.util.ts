import type {
  CoverageCount,
  StoryProgress,
} from "@/modules/traceability/typing/types/traceability.type";

export const LAST_RUN_ID = "f1000000-0000-4000-8000-000000000001";

export const buildCoverage = (overrides: Partial<CoverageCount> = {}): CoverageCount => {
  return {
    criterionCount: 3,
    coveredCount: 2,
    passedCount: 1,
    failedCount: 1,
    blockedCount: 0,
    notRunCount: 0,
    uncoveredCount: 1,
    ...overrides,
  };
};

export const buildStoryProgress = (overrides: Partial<StoryProgress> = {}): StoryProgress => {
  return {
    storyId: "c1000000-0000-4000-8000-000000000001",
    jiraKey: "SHOP-1",
    coverage: buildCoverage(),
    openGapCount: 2,
    activeFailureCount: 1,
    lastRun: {
      id: LAST_RUN_ID,
      status: "failed",
      startedAt: "2026-10-20T09:00:00Z",
      finishedAt: "2026-10-20T09:30:00Z",
    },
    ...overrides,
  };
};
