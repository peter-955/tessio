"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { LabelCoverageReport } from "../../typing/types/insights.type";

export const GET_LABEL_COVERAGE_KEY = "GET_LABEL_COVERAGE_KEY";

export type GetLabelCoverageQueryKey = [typeof GET_LABEL_COVERAGE_KEY, string];

type Result = Pick<
  UseQueryResult<LabelCoverageReport, ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetLabelCoverage = (projectKey: string): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    LabelCoverageReport,
    GetLabelCoverageQueryKey
  >({
    queryKey: [GET_LABEL_COVERAGE_KEY, projectKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/insights/coverage-by-label", {
          params: { path: { project_key: projectKey } },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError, isFetching, refetch };
};
