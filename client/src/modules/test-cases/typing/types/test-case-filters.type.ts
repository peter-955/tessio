import type { TestCasePriority, TestCaseStatus } from "./test-case.type";

export interface TestCaseFilters {
  storyKey: string | null;
  status: TestCaseStatus | null;
  priority: TestCasePriority | null;
  criterionId: string | null;
  isNeedingReview: boolean;
  query: string;
}

export interface TestCaseListQuery {
  storyKey?: string;
  status?: TestCaseStatus;
  priority?: TestCasePriority;
  criterionId?: string;
  needsReview?: boolean;
  query?: string;
}

export type TestCaseSearchParams = Record<string, string | string[] | undefined>;
