import type { AssignableWorkspaceRole } from "./workspace-user.type";

export interface InviteUserValues {
  email: string;
  name: string;
  workspaceRole: AssignableWorkspaceRole;
}
