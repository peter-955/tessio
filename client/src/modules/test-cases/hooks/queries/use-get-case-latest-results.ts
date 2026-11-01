"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import type { CaseLatestResult } from "@/modules/traceability/typing/types/traceability.type";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { keepPreviousData, type UseQueryResult } from "@tanstack/react-query";

export const GET_CASE_LATEST_RESULTS_KEY = "GET_CASE_LATEST_RESULTS_KEY";

export type GetCaseLatestResultsQueryKey = [
  typeof GET_CASE_LATEST_RESULTS_KEY,
  string,
  string | null,
];

type Result = Pick<UseQueryResult<CaseLatestResult[], ApiError>, "data" | "isPending" | "isError">;

export const useGetCaseLatestResults = (projectKey: string, storyKey: string | null): Result => {
  const { data, isPending, isError } = useAppQuery<
    CaseLatestResult[],
    GetCaseLatestResultsQueryKey
  >({
    queryKey: [GET_CASE_LATEST_RESULTS_KEY, projectKey, storyKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/case-latest-results", {
          params: {
            path: { project_key: projectKey },
            query: storyKey === null ? {} : { storyKey },
          },
          signal,
        }),
      );
    },
    placeholderData: keepPreviousData,
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError };
};
