"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { RunDetail } from "@/shared/typing/types/test-run.type";
import type { UseQueryResult } from "@tanstack/react-query";
import { RUN_POLL_INTERVAL_IN_MILLISECONDS } from "../../typing/constants/run.constant";

export const GET_RUN_KEY = "GET_RUN_KEY";

export type GetRunQueryKey = [typeof GET_RUN_KEY, string, string];

type Result = Pick<
  UseQueryResult<RunDetail, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetRun = (projectKey: string, runId: string, isEnabled = true): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    RunDetail,
    GetRunQueryKey
  >({
    queryKey: [GET_RUN_KEY, projectKey, runId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/runs/{run_id}", {
          params: { path: { project_key: projectKey, run_id: runId } },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    refetchInterval: (query) => {
      return query.state.data?.status === "running" ? RUN_POLL_INTERVAL_IN_MILLISECONDS : false;
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
