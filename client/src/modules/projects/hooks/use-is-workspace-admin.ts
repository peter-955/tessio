"use client";

import { checkIsWorkspaceAdmin } from "@/components/app-shell/utils/workspace-role.util";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";

export const useIsWorkspaceAdmin = (): boolean => {
  return checkIsWorkspaceAdmin(useCurrentUser().workspaceRole);
};
