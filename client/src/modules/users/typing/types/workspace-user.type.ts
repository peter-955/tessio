import type { components } from "@/lib/api/openapi.type";

export type WorkspaceUser = components["schemas"]["WorkspaceUserResponse"];

export type UserProjectAccess = components["schemas"]["UserProjectAccessResponse"];

export type UserStatus = components["schemas"]["UserStatus"];

export type WorkspaceRole = components["schemas"]["WorkspaceRole"];

export type ProjectRole = components["schemas"]["ProjectRole"];

export type AssignableWorkspaceRole = components["schemas"]["InviteUserRequest"]["workspaceRole"];

export type InviteUserRequest = components["schemas"]["InviteUserRequest"];

export interface UserActor {
  id: string;
  workspaceRole: WorkspaceRole;
}
