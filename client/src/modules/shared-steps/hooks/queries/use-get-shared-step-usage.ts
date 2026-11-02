"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { SharedStepUsage } from "../../typing/types/shared-step.type";

export const GET_SHARED_STEP_USAGE_KEY = "GET_SHARED_STEP_USAGE_KEY";

export type GetSharedStepUsageQueryKey = [typeof GET_SHARED_STEP_USAGE_KEY, string, string];

type Result = Pick<
  UseQueryResult<SharedStepUsage[], ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetSharedStepUsage = (projectKey: string, sharedStepKey: string): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    SharedStepUsage[],
    GetSharedStepUsageQueryKey
  >({
    queryKey: [GET_SHARED_STEP_USAGE_KEY, projectKey, sharedStepKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/shared-steps/{key}/usage", {
          params: { path: { project_key: projectKey, key: sharedStepKey } },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError, isFetching, refetch };
};
