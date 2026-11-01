"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { READY_STATUS } from "../../typing/constants/manual-run.constant";
import type { ReadyTestCase } from "../../typing/types/manual-run.type";

export const GET_READY_TEST_CASES_KEY = "GET_READY_TEST_CASES_KEY";

export type GetReadyTestCasesQueryKey = [typeof GET_READY_TEST_CASES_KEY, string, string | null];

type Result = Pick<
  UseQueryResult<ReadyTestCase[], ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetReadyTestCases = (projectKey: string, storyKey: string | null): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    ReadyTestCase[],
    GetReadyTestCasesQueryKey
  >({
    queryKey: [GET_READY_TEST_CASES_KEY, projectKey, storyKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/test-cases", {
          params: {
            path: { project_key: projectKey },
            query: { storyKey, status: READY_STATUS },
          },
          signal,
        }),
      );
    },
    enabled: storyKey !== null,
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending: storyKey !== null && isPending, isError, isFetching, refetch };
};
