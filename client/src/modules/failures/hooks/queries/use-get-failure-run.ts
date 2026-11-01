"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { SCREENSHOT_POLL_MILLISECONDS } from "../../typing/constants/failure.constant";
import type { FailureRun } from "../../typing/types/failure.type";

export const GET_FAILURE_RUN_KEY = "GET_FAILURE_RUN_KEY";

export type GetFailureRunQueryKey = [typeof GET_FAILURE_RUN_KEY, string, string];

type Result = Pick<UseQueryResult<FailureRun, ApiError>, "data" | "isPending" | "isError">;

export const useGetFailureRun = (
  projectKey: string,
  runId: string,
  isEnabled: boolean,
  checkIsPolling: (run: FailureRun) => boolean,
): Result => {
  const { data, isPending, isError } = useAppQuery<FailureRun, GetFailureRunQueryKey>({
    queryKey: [GET_FAILURE_RUN_KEY, projectKey, runId],
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
      const run = query.state.data;

      return run !== undefined && checkIsPolling(run) ? SCREENSHOT_POLL_MILLISECONDS : false;
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError };
};
