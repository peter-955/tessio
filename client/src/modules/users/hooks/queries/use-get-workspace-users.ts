"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { keepPreviousData, type UseQueryResult } from "@tanstack/react-query";
import type { UserFilters } from "../../typing/types/user-filters.type";
import type {
  UserStatus,
  WorkspaceRole,
  WorkspaceUser,
} from "../../typing/types/workspace-user.type";
import { buildUserListQuery } from "../../utils/user-filters.util";

export const GET_WORKSPACE_USERS_KEY = "GET_WORKSPACE_USERS_KEY";

export type GetWorkspaceUsersQueryKey = [
  typeof GET_WORKSPACE_USERS_KEY,
  UserStatus | null,
  WorkspaceRole | null,
  string,
];

type Result = Pick<
  UseQueryResult<WorkspaceUser[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetWorkspaceUsers = (filters: UserFilters, isEnabled: boolean): Result => {
  const trimmedQuery = filters.query.trim();
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    WorkspaceUser[],
    GetWorkspaceUsersQueryKey
  >({
    queryKey: [GET_WORKSPACE_USERS_KEY, filters.status, filters.workspaceRole, trimmedQuery],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/users", {
          params: { query: buildUserListQuery(filters) },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    placeholderData: keepPreviousData,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
