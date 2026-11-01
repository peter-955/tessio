"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { UserProjectAccess } from "../../typing/types/workspace-user.type";

export const GET_USER_ACCESS_KEY = "GET_USER_ACCESS_KEY";

export type GetUserAccessQueryKey = [typeof GET_USER_ACCESS_KEY, string];

type Result = Pick<
  UseQueryResult<UserProjectAccess[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetUserAccess = (userId: string, isEnabled = true): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    UserProjectAccess[],
    GetUserAccessQueryKey
  >({
    queryKey: [GET_USER_ACCESS_KEY, userId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/users/{user_id}/access", {
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
