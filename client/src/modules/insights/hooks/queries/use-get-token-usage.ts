"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { InsightsRange } from "../../typing/types/insights-range.type";
import type { TokenUsage } from "../../typing/types/insights.type";

export const GET_TOKEN_USAGE_KEY = "GET_TOKEN_USAGE_KEY";

export type GetTokenUsageQueryKey = [typeof GET_TOKEN_USAGE_KEY, string, string, string];

type Result = Pick<
  UseQueryResult<TokenUsage, ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetTokenUsage = (projectKey: string, range: InsightsRange): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    TokenUsage,
    GetTokenUsageQueryKey
  >({
    queryKey: [GET_TOKEN_USAGE_KEY, projectKey, range.from, range.to],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/insights/tokens", {
          params: {
            path: { project_key: projectKey },
            query: { from: range.from, to: range.to },
          },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError, isFetching, refetch };
};
