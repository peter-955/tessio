import type { UserProjectAccess, WorkspaceUser } from "../../typing/types/workspace-user.type";

export const OWNER_ID = "1f0c7a52-0b3e-4d6a-9f1e-6c2b8d4e0a01";

export const ADMIN_ID = "2a1d8b63-1c4f-4e7b-8a2f-7d3c9e5f1b02";

export const MEMBER_ID = "3b2e9c74-2d5a-4f8c-9b3a-8e4d0f6a2c03";

export const createWorkspaceUser = (overrides: Partial<WorkspaceUser> = {}): WorkspaceUser => {
  return {
    id: MEMBER_ID,
    email: "lan@example.test",
    name: "Lan Nguyen",
    workspaceRole: "member",
    status: "active",
    isTwoFactorSetUp: true,
    avatarUrl: null,
    createdAt: "2026-10-01T09:00:00Z",
    deactivatedAt: null,
    ...overrides,
  };
};

export const createUserProjectAccess = (
  overrides: Partial<UserProjectAccess> = {},
): UserProjectAccess => {
  return {
    projectId: "4c3f0d85-3e6b-4a9d-8c4b-9f5e1a7b3d04",
    projectKey: "SHOP",
    projectName: "Shop checkout",
    role: "qc",
    isArchived: false,
    ...overrides,
  };
};
