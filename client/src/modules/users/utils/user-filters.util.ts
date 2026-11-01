import type { UserFilters, UserListQuery } from "../typing/types/user-filters.type";

export const buildUserListQuery = (filters: UserFilters): UserListQuery => {
  const trimmedQuery = filters.query.trim();

  return {
    ...(filters.status === null ? {} : { status: filters.status }),
    ...(filters.workspaceRole === null ? {} : { workspaceRole: filters.workspaceRole }),
    ...(trimmedQuery === "" ? {} : { query: trimmedQuery }),
  };
};
