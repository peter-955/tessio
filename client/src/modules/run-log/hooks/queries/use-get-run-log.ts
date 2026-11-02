"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { RunLog } from "../../typing/types/run-log.type";

export const GET_RUN_LOG_KEY = "GET_RUN_LOG_KEY";

export type GetRunLogQueryKey = [typeof GET_RUN_LOG_KEY, string, string];

type Result = Pick<
  UseQueryResult<RunLog, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch" | "dataUpdatedAt"
>;

export const useGetRunLog = (projectKey: string, runId: string, isEnabled = true): Result => {
  const { data, error, isPending, isError, isFetching, refetch, dataUpdatedAt } = useAppQuery<
    RunLog,
    GetRunLogQueryKey
  >({
    queryKey: [GET_RUN_LOG_KEY, projectKey, runId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/runs/{run_id}/log", {
          params: { path: { project_key: projectKey, run_id: runId } },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch, dataUpdatedAt };
};
