"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { CASE_LIST_LIMIT } from "../../typing/constants/insights.constant";
import type { FlakyCase } from "../../typing/types/insights.type";

export const GET_FLAKY_CASES_KEY = "GET_FLAKY_CASES_KEY";

export type GetFlakyCasesQueryKey = [typeof GET_FLAKY_CASES_KEY, string];

type Result = Pick<
  UseQueryResult<FlakyCase[], ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetFlakyCases = (projectKey: string): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    FlakyCase[],
    GetFlakyCasesQueryKey
  >({
    queryKey: [GET_FLAKY_CASES_KEY, projectKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/insights/flaky", {
          params: { path: { project_key: projectKey }, query: { limit: CASE_LIST_LIMIT } },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError, isFetching, refetch };
};
