"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { keepPreviousData, type UseQueryResult } from "@tanstack/react-query";
import type { TestCaseFilters } from "../../typing/types/test-case-filters.type";
import type {
  TestCasePriority,
  TestCaseStatus,
  TestCaseSummary,
} from "../../typing/types/test-case.type";
import { buildTestCaseListQuery } from "../../utils/test-case-filters.util";

export const GET_TEST_CASES_KEY = "GET_TEST_CASES_KEY";

export type GetTestCasesQueryKey = [
  typeof GET_TEST_CASES_KEY,
  string,
  string | null,
  TestCaseStatus | null,
  TestCasePriority | null,
  string | null,
  boolean,
  string,
];

type Result = Pick<
  UseQueryResult<TestCaseSummary[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetTestCases = (projectKey: string, filters: TestCaseFilters): Result => {
  const trimmedQuery = filters.query.trim();
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    TestCaseSummary[],
    GetTestCasesQueryKey
  >({
    queryKey: [
      GET_TEST_CASES_KEY,
      projectKey,
      filters.storyKey,
      filters.status,
      filters.priority,
      filters.criterionId,
      filters.isNeedingReview,
      trimmedQuery,
    ],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/test-cases", {
          params: { path: { project_key: projectKey }, query: buildTestCaseListQuery(filters) },
          signal,
        }),
      );
    },
    placeholderData: keepPreviousData,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
