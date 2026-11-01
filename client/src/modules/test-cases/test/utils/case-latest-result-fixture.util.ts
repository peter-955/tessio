import type {
  CaseLatestResult,
  LatestResult,
} from "@/modules/traceability/typing/types/traceability.type";
import { STORY_ID } from "./test-case-fixture.util";

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

export const buildCaseLatestResult = (
  overrides: Partial<CaseLatestResult> = {},
): CaseLatestResult => {
  return {
    caseId: "e1000000-0000-4000-8000-000000000001",
    code: "TC-1",
    storyId: STORY_ID,
    latestResult: buildLatestResult(),
    ...overrides,
  };
};
