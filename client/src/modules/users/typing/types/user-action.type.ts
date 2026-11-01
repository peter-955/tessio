import type { WorkspaceUser } from "./workspace-user.type";

export type UserConfirmAction = "deactivate" | "reactivate" | "resetTwoFactor";

export interface UserConfirmTarget {
  user: WorkspaceUser;
  action: UserConfirmAction;
}
