import type { DSBadgeColor } from "@/components/design-system";
import type {
  AssignableWorkspaceRole,
  UserStatus,
  WorkspaceRole,
} from "../types/workspace-user.type";

export const USER_STATUSES: UserStatus[] = ["invited", "active", "deactivated"];

export const WORKSPACE_ROLES: WorkspaceRole[] = ["owner", "admin", "member"];

export const ASSIGNABLE_WORKSPACE_ROLES: AssignableWorkspaceRole[] = ["admin", "member"];

export const USERS_PATH = "/users";

export const SEARCH_DEBOUNCE_MILLISECONDS = 300;

export const MAX_USER_QUERY_LENGTH = 100;

export const MAX_USER_NAME_LENGTH = 100;

export const MAX_EMAIL_LENGTH = 320;

export const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export const INVITE_USER_FORM_ID = "invite-user-form";

export const NOT_FOUND_STATUS = 404;

export const USER_STATUS_BADGE_COLORS: Record<UserStatus, DSBadgeColor> = {
  invited: "yellow",
  active: "green",
  deactivated: "gray",
};

export const WORKSPACE_ROLE_BADGE_COLORS: Record<WorkspaceRole, DSBadgeColor> = {
  owner: "tessio",
  admin: "tessio",
  member: "gray",
};
