"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { CASE_LIST_LIMIT } from "../../typing/constants/insights.constant";
import type { InsightsRange } from "../../typing/types/insights-range.type";
import type { FailingCase } from "../../typing/types/insights.type";

export const GET_TOP_FAILING_CASES_KEY = "GET_TOP_FAILING_CASES_KEY";

export type GetTopFailingCasesQueryKey = [typeof GET_TOP_FAILING_CASES_KEY, string, string, string];

type Result = Pick<
  UseQueryResult<FailingCase[], ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetTopFailingCases = (projectKey: string, range: InsightsRange): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    FailingCase[],
    GetTopFailingCasesQueryKey
  >({
    queryKey: [GET_TOP_FAILING_CASES_KEY, projectKey, range.from, range.to],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/insights/top-failing", {
          params: {
            path: { project_key: projectKey },
            query: { from: range.from, to: range.to, limit: CASE_LIST_LIMIT },
          },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError, isFetching, refetch };
};
