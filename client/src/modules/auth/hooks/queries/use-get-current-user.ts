"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { CurrentUser } from "../../typing/types/current-user.type";

export const GET_CURRENT_USER_KEY = "GET_CURRENT_USER_KEY";

type GetCurrentUserKey = [typeof GET_CURRENT_USER_KEY];

type Result = Pick<
  UseQueryResult<CurrentUser, ApiError>,
  "data" | "error" | "isPending" | "isError" | "refetch" | "isRefetching"
>;

export const useGetCurrentUser = (): Result => {
  const { data, error, isPending, isError, refetch, isRefetching } = useAppQuery<
    CurrentUser,
    GetCurrentUserKey
  >({
    queryKey: [GET_CURRENT_USER_KEY],
    queryFn: ({ signal }) => {
      return unwrapResponse(apiClient.GET("/api/auth/me", { signal }));
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, refetch, isRefetching };
};
