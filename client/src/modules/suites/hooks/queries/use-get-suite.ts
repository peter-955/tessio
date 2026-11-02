"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { SuiteDetail } from "../../typing/types/suite.type";

export const GET_SUITE_KEY = "GET_SUITE_KEY";

export type GetSuiteQueryKey = [typeof GET_SUITE_KEY, string, string | null];

type Result = Pick<
  UseQueryResult<SuiteDetail, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetSuite = (
  projectKey: string,
  suiteId: string | null,
  isEnabled = true,
): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    SuiteDetail,
    GetSuiteQueryKey
  >({
    queryKey: [GET_SUITE_KEY, projectKey, suiteId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/suites/{suite_id}", {
          params: { path: { project_key: projectKey, suite_id: suiteId ?? "" } },
          signal,
        }),
      );
    },
    enabled: isEnabled && suiteId !== null,
    isGlobalErrorToastDisabled: true,
  });

  return {
    data,
    error,
    isPending: suiteId !== null && isEnabled && isPending,
    isError,
    isFetching,
    refetch,
  };
};
