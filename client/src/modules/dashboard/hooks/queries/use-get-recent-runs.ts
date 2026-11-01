"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { RECENT_RUNS_LIMIT } from "../../typing/constants/dashboard.constant";
import type { RecentRun } from "../../typing/types/recent-run.type";

export const GET_RECENT_RUNS_KEY = "GET_RECENT_RUNS_KEY";

export type GetRecentRunsQueryKey = [typeof GET_RECENT_RUNS_KEY, string];

type Result = Pick<
  UseQueryResult<RecentRun[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetRecentRuns = (projectKey: string): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    RecentRun[],
    GetRecentRunsQueryKey
  >({
    queryKey: [GET_RECENT_RUNS_KEY, projectKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/runs", {
          params: { path: { project_key: projectKey }, query: { limit: RECENT_RUNS_LIMIT } },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
