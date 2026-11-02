"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { InsightsRange } from "../../typing/types/insights-range.type";
import type { InsightTrends, TrendGrouping } from "../../typing/types/insights.type";

export const GET_INSIGHT_TRENDS_KEY = "GET_INSIGHT_TRENDS_KEY";

export type GetInsightTrendsQueryKey = [
  typeof GET_INSIGHT_TRENDS_KEY,
  string,
  string,
  string,
  TrendGrouping,
];

type Result = Pick<
  UseQueryResult<InsightTrends, ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetInsightTrends = (
  projectKey: string,
  range: InsightsRange,
  groupBy: TrendGrouping,
): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    InsightTrends,
    GetInsightTrendsQueryKey
  >({
    queryKey: [GET_INSIGHT_TRENDS_KEY, projectKey, range.from, range.to, groupBy],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/insights/trends", {
          params: {
            path: { project_key: projectKey },
            query: { from: range.from, to: range.to, groupBy },
          },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError, isFetching, refetch };
};
