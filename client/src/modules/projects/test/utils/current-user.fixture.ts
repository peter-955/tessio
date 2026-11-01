import type { WorkspaceRole } from "@/components/app-shell/typing/types/workspace-role.type";
import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";

export const CURRENT_USER_ID = "0b7f4a8e-3c55-4f5e-8f3e-2a0c9f1d6b21";

export const buildCurrentUser = (workspaceRole: WorkspaceRole): CurrentUser => {
  return {
    id: CURRENT_USER_ID,
    email: "lan@example.com",
    name: "Lan Nguyen",
    workspaceRole,
    nextStep: "signed_in",
    language: "en",
    colorScheme: "auto",
    avatarFileId: null,
    avatarUrl: null,
    isTwoFactorSetUp: true,
  };
};
