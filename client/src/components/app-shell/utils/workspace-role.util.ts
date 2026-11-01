import type { WorkspaceRole } from "../typing/types/workspace-role.type";

export const checkIsWorkspaceAdmin = (role: WorkspaceRole): boolean => {
  return role === "owner" || role === "admin";
};
