"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { WorkspaceUser } from "../../typing/types/workspace-user.type";

export const GET_WORKSPACE_USER_KEY = "GET_WORKSPACE_USER_KEY";

export type GetWorkspaceUserQueryKey = [typeof GET_WORKSPACE_USER_KEY, string];

type Result = Pick<
  UseQueryResult<WorkspaceUser, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetWorkspaceUser = (userId: string, isEnabled = true): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    WorkspaceUser,
    GetWorkspaceUserQueryKey
  >({
    queryKey: [GET_WORKSPACE_USER_KEY, userId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/users/{user_id}", {
          params: { path: { user_id: userId } },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
