import type { TestCasePriority, TestCaseStatus } from "./test-case.type";

export interface TestCaseFilters {
  storyKey: string | null;
  status: TestCaseStatus | null;
  priority: TestCasePriority | null;
  criterionId: string | null;
  isNeedingReview: boolean;
  isFlaky: boolean;
  isDisagreeing: boolean;
  isQuarantined: boolean;
  labelNames: string[];
  query: string;
}

export interface TestCaseListQuery {
  storyKey?: string;
  status?: TestCaseStatus;
  priority?: TestCasePriority;
  criterionId?: string;
  needsReview?: boolean;
  flaky?: boolean;
  disagreeing?: boolean;
  quarantined?: boolean;
  label?: string[];
  query?: string;
}

export type TestCaseSearchParams = Record<string, string | string[] | undefined>;
