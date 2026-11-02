import type { Notification, NotificationPage } from "../../typing/types/notification.type";

const PROJECT_FIELDS = {
  projectId: "5f0c2b7e-4a3d-4e8f-9b1a-2c3d4e5f6a01",
  projectKey: "TES",
  projectName: "Tessio",
  actorId: "6a1d3c8f-5b4e-4f9a-8c2b-3d4e5f6a7b02",
  actorName: "Lan Nguyen",
  isRead: false,
  readAt: null,
  createdAt: "2026-11-01T09:55:00Z",
} as const;

export const createGapNotification = (overrides: Partial<Notification> = {}): Notification => {
  return {
    ...PROJECT_FIELDS,
    id: "7b2e4d9a-6c5f-4a0b-9d3c-4e5f6a7b8c03",
    kind: "gap_assigned",
    payload: {
      kind: "gap_assigned",
      gapId: "8c3f5e0b-7d6a-4b1c-8e4d-5f6a7b8c9d04",
      storyId: "9d4a6f1c-8e7b-4c2d-9f5e-6a7b8c9d0e05",
      storyJiraKey: "TES-42",
      question: "Which currency applies to refunds?",
    },
    ...overrides,
  };
};

export const createFailureNotification = (overrides: Partial<Notification> = {}): Notification => {
  return {
    ...PROJECT_FIELDS,
    id: "0e5b7a2d-9f8c-4d3e-8a6f-7b8c9d0e1f06",
    kind: "failure_assigned",
    payload: {
      kind: "failure_assigned",
      failureId: "1f6c8b3e-0a9d-4e4f-9b7a-8c9d0e1f2a07",
      testCaseId: "2a7d9c4f-1b0e-4f5a-8c8b-9d0e1f2a3b08",
      testCaseCode: "TC-7",
      testCaseTitle: "Refund in euros",
      storyJiraKey: "TES-43",
    },
    ...overrides,
  };
};

export const createRunNotification = (overrides: Partial<Notification> = {}): Notification => {
  return {
    ...PROJECT_FIELDS,
    id: "3b8e0d5a-2c1f-4a6b-9d9c-0e1f2a3b4c09",
    kind: "run_finished",
    payload: {
      kind: "run_finished",
      runId: "4c9f1e6b-3d2a-4b7c-8e0d-1f2a3b4c5d10",
      storyId: "5d0a2f7c-4e3b-4c8d-9f1e-2a3b4c5d6e11",
      storyJiraKey: "TES-44",
      outcome: "failed",
      passedCount: 5,
      failedCount: 2,
      blockedCount: 1,
    },
    ...overrides,
  };
};

export const createSuiteRunNotification = (overrides: Partial<Notification> = {}): Notification => {
  return {
    ...PROJECT_FIELDS,
    id: "6e1b3a8d-5f4c-4d9e-8b2a-3c4d5e6f7a12",
    kind: "suite_run_finished",
    payload: {
      kind: "suite_run_finished",
      runId: "7f2c4b9e-6a5d-4e0f-9c3b-4d5e6f7a8b13",
      testSuiteId: "8a3d5c0f-7b6e-4f1a-8d4c-5e6f7a8b9c14",
      testSuiteName: "Checkout regression",
      outcome: "passed",
      passedCount: 12,
      failedCount: 0,
      blockedCount: 0,
    },
    ...overrides,
  };
};

export const createReportNotification = (overrides: Partial<Notification> = {}): Notification => {
  return {
    ...PROJECT_FIELDS,
    id: "9b4e6d1a-8c7f-4a2b-9e5d-6f7a8b9c0d15",
    kind: "report_ready",
    payload: {
      kind: "report_ready",
      fileId: "0c5f7e2b-9d8a-4b3c-8f6e-7a8b9c0d1e16",
      fileName: "story-TES-42.pdf",
      format: "pdf",
      source: "story",
      sourceId: "TES-42",
      sourceLabel: "TES-42 Refund a payment",
    },
    ...overrides,
  };
};

export const createNotificationPage = (
  items: Notification[],
  nextCursor: string | null = null,
): NotificationPage => {
  return { items, nextCursor };
};
