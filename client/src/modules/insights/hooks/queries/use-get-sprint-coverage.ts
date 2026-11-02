"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { InsightsRange } from "../../typing/types/insights-range.type";
import type { SprintCoverage } from "../../typing/types/insights.type";

export const GET_SPRINT_COVERAGE_KEY = "GET_SPRINT_COVERAGE_KEY";

export type GetSprintCoverageQueryKey = [typeof GET_SPRINT_COVERAGE_KEY, string, string, string];

type Result = Pick<
  UseQueryResult<SprintCoverage[], ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetSprintCoverage = (projectKey: string, range: InsightsRange): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    SprintCoverage[],
    GetSprintCoverageQueryKey
  >({
    queryKey: [GET_SPRINT_COVERAGE_KEY, projectKey, range.from, range.to],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/insights/sprint-coverage", {
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
