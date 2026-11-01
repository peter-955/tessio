import type { UserStatus, WorkspaceRole } from "./workspace-user.type";

export interface UserFilters {
  status: UserStatus | null;
  workspaceRole: WorkspaceRole | null;
  query: string;
}

export interface UserListQuery {
  status?: UserStatus;
  workspaceRole?: WorkspaceRole;
  query?: string;
}
