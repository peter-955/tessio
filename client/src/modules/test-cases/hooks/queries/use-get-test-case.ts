"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { TestCaseDetail } from "../../typing/types/test-case.type";

export const GET_TEST_CASE_KEY = "GET_TEST_CASE_KEY";

export type GetTestCaseQueryKey = [typeof GET_TEST_CASE_KEY, string, string];

type Result = Pick<
  UseQueryResult<TestCaseDetail, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetTestCase = (projectKey: string, caseCode: string, isEnabled = true): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    TestCaseDetail,
    GetTestCaseQueryKey
  >({
    queryKey: [GET_TEST_CASE_KEY, projectKey, caseCode],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/test-cases/{case_code}", {
          params: { path: { project_key: projectKey, case_code: caseCode } },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
