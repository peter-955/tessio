"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { ApiToken } from "../../typing/types/api-token.type";

export const GET_API_TOKENS_KEY = "GET_API_TOKENS_KEY";

type GetApiTokensKey = [typeof GET_API_TOKENS_KEY];

type Result = Pick<
  UseQueryResult<ApiToken[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "refetch" | "isRefetching"
>;

export const useGetApiTokens = (): Result => {
  const { data, error, isPending, isError, refetch, isRefetching } = useAppQuery<
    ApiToken[],
    GetApiTokensKey
  >({
    queryKey: [GET_API_TOKENS_KEY],
    queryFn: ({ signal }) => {
      return unwrapResponse(apiClient.GET("/api/me/api-tokens", { signal }));
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, refetch, isRefetching };
};
