import { ASSIGNABLE_WORKSPACE_ROLES } from "../typing/constants/user.constant";
import type { AssignableWorkspaceRole, WorkspaceRole } from "../typing/types/workspace-user.type";

export const findAssignableWorkspaceRole = (
  role: WorkspaceRole,
): AssignableWorkspaceRole | null => {
  return (
    ASSIGNABLE_WORKSPACE_ROLES.find((assignableRole) => {
      return assignableRole === role;
    }) ?? null
  );
};
