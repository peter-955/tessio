import type {
  SharedStep,
  SharedStepUsage,
  SharedStepVersion,
} from "../../typing/types/shared-step.type";

export const SHARED_STEP_ID = "e1000000-0000-4000-8000-000000000001";

export const ARCHIVED_SHARED_STEP_ID = "e1000000-0000-4000-8000-000000000002";

export const QC_USER_ID = "e9000000-0000-4000-8000-000000000001";

export const buildSharedStepVersion = (
  overrides: Partial<SharedStepVersion> = {},
): SharedStepVersion => {
  return {
    id: "e2000000-0000-4000-8000-000000000001",
    number: 2,
    steps: [
      { order: 1, action: "Open the sign-in page", expected: null },
      {
        order: 2,
        action: "Sign in as {{data.admin_email}}",
        expected: "The dashboard shows",
      },
    ],
    dataKeys: ["admin_email"],
    createdBy: QC_USER_ID,
    createdAt: "2026-10-28T10:00:00Z",
    ...overrides,
  };
};

export const buildSharedStep = (overrides: Partial<SharedStep> = {}): SharedStep => {
  return {
    id: SHARED_STEP_ID,
    key: "login_as_admin",
    title: "Log in as admin",
    isArchived: false,
    archivedAt: null,
    currentVersion: buildSharedStepVersion(),
    usageCount: 3,
    createdBy: QC_USER_ID,
    createdAt: "2026-10-20T10:00:00Z",
    ...overrides,
  };
};

export const ARCHIVED_SHARED_STEP = buildSharedStep({
  id: ARCHIVED_SHARED_STEP_ID,
  key: "old_login",
  title: "Old login",
  isArchived: true,
  archivedAt: "2026-10-25T10:00:00Z",
  usageCount: 1,
  currentVersion: buildSharedStepVersion({
    id: "e2000000-0000-4000-8000-000000000002",
    number: 1,
    steps: [{ order: 1, action: "Use the old login form", expected: null }],
    dataKeys: [],
  }),
});

export const buildSharedStepUsage = (overrides: Partial<SharedStepUsage> = {}): SharedStepUsage => {
  return {
    testCaseId: "e3000000-0000-4000-8000-000000000001",
    code: "TC-4",
    title: "Refund an order",
    status: "ready",
    storyJiraKey: "SHOP-2",
    versionNumber: 3,
    ...overrides,
  };
};
