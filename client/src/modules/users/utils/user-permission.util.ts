import type { UserActor, WorkspaceRole, WorkspaceUser } from "../typing/types/workspace-user.type";

export const checkIsWorkspaceAdmin = (role: WorkspaceRole): boolean => {
  return role === "owner" || role === "admin";
};

export const checkCanManageUser = (actor: UserActor, target: WorkspaceUser): boolean => {
  if (target.id === actor.id || target.workspaceRole === "owner") {
    return false;
  }

  if (target.workspaceRole === "admin") {
    return actor.workspaceRole === "owner";
  }

  return checkIsWorkspaceAdmin(actor.workspaceRole);
};

export const checkCanChangeRole = (actor: UserActor, target: WorkspaceUser): boolean => {
  return checkCanManageUser(actor, target) && actor.workspaceRole === "owner";
};
