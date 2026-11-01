"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { ManualRun } from "../../typing/types/manual-run.type";

export const GET_MANUAL_RUN_KEY = "GET_MANUAL_RUN_KEY";

export type GetManualRunQueryKey = [typeof GET_MANUAL_RUN_KEY, string, string];

type Result = Pick<
  UseQueryResult<ManualRun, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetManualRun = (projectKey: string, runId: string, isEnabled: boolean): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    ManualRun,
    GetManualRunQueryKey
  >({
    queryKey: [GET_MANUAL_RUN_KEY, projectKey, runId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/runs/{run_id}", {
          params: { path: { project_key: projectKey, run_id: runId } },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
