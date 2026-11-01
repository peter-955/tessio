"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { RunSummary } from "@/shared/typing/types/test-run.type";
import { keepPreviousData, type UseQueryResult } from "@tanstack/react-query";
import type { RunFilters, RunListQuery } from "../../typing/types/run.type";
import { buildRunListQuery } from "../../utils/run-filters.util";

export const GET_RUNS_KEY = "GET_RUNS_KEY";

export type GetRunsQueryKey = [typeof GET_RUNS_KEY, string, RunListQuery];

type Result = Pick<
  UseQueryResult<RunSummary[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetRuns = (projectKey: string, filters: RunFilters): Result => {
  const query = buildRunListQuery(filters);
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    RunSummary[],
    GetRunsQueryKey
  >({
    queryKey: [GET_RUNS_KEY, projectKey, query],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/runs", {
          params: { path: { project_key: projectKey }, query },
          signal,
        }),
      );
    },
    placeholderData: keepPreviousData,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
