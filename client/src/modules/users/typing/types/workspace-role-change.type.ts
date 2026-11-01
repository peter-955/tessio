import type { AssignableWorkspaceRole } from "./workspace-user.type";

export interface WorkspaceRoleChange {
  userId: string;
  workspaceRole: AssignableWorkspaceRole;
}
