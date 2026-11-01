import type { Sprint } from "../../typing/types/sprint.type";

export const ACTIVE_SPRINT_ID = "5a1e2b3c-4d5e-4f60-8a1b-2c3d4e5f6a70";

export const FUTURE_SPRINT_ID = "6b2f3c4d-5e6f-4a71-9b2c-3d4e5f6a7b81";

export const CLOSED_SPRINT_ID = "7c3a4d5e-6f7a-4b82-8c3d-4e5f6a7b8c92";

export const buildSprint = (overrides: Partial<Sprint> = {}): Sprint => {
  return {
    id: ACTIVE_SPRINT_ID,
    jiraSprintId: 12,
    name: "Sprint 12",
    state: "active",
    startAt: "2026-10-14T00:00:00Z",
    endAt: "2026-10-28T00:00:00Z",
    completeAt: null,
    storyCount: 4,
    syncedAt: "2026-10-20T09:00:00Z",
    ...overrides,
  };
};
