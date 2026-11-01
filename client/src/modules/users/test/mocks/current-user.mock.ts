import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import type { WorkspaceRole } from "../../typing/types/workspace-user.type";
import { ADMIN_ID, MEMBER_ID, OWNER_ID } from "../utils/workspace-user.fixture";

const CURRENT_USER_IDS: Record<WorkspaceRole, string> = {
  owner: OWNER_ID,
  admin: ADMIN_ID,
  member: MEMBER_ID,
};

export const currentUserState: { workspaceRole: WorkspaceRole } = { workspaceRole: "owner" };

export const setCurrentUserRole = (workspaceRole: WorkspaceRole): void => {
  currentUserState.workspaceRole = workspaceRole;
};

export const currentUserMock = {
  useCurrentUser: (): CurrentUser => {
    return {
      id: CURRENT_USER_IDS[currentUserState.workspaceRole],
      email: "current@example.test",
      name: "Current User",
      workspaceRole: currentUserState.workspaceRole,
      nextStep: "signed_in",
      language: "en",
      colorScheme: "auto",
      avatarFileId: null,
      avatarUrl: null,
      isTwoFactorSetUp: true,
    };
  },
};
