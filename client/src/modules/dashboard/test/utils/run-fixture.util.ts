import type { RecentRun } from "../../typing/types/recent-run.type";

export const RUN_ID = "e1000000-0000-4000-8000-000000000001";

export const ABORTED_RUN_ID = "e1000000-0000-4000-8000-000000000002";

export const buildRecentRun = (overrides: Partial<RecentRun> = {}): RecentRun => {
  return {
    id: RUN_ID,
    storyId: "c1000000-0000-4000-8000-000000000001",
    storyJiraKey: "SHOP-1",
    storyTitle: "Pay by card",
    environmentId: "a2000000-0000-4000-8000-000000000001",
    environmentName: "Staging",
    executor: "claude",
    status: "passed",
    abortReason: null,
    parentRunId: null,
    startedBy: "a3000000-0000-4000-8000-000000000001",
    startedByName: "Ana Tester",
    startedAt: "2026-10-22T08:00:00Z",
    finishedAt: "2026-10-22T08:10:00Z",
    counts: { total: 6, passed: 5, failed: 1, blocked: 0, skipped: 0, notReported: 0 },
    ...overrides,
  };
};
