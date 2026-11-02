"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { SharedStep } from "../../typing/types/shared-step.type";

export const GET_SHARED_STEP_KEY = "GET_SHARED_STEP_KEY";

export type GetSharedStepQueryKey = [typeof GET_SHARED_STEP_KEY, string, string];

type Result = Pick<
  UseQueryResult<SharedStep, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetSharedStep = (
  projectKey: string,
  sharedStepKey: string,
  isEnabled = true,
): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    SharedStep,
    GetSharedStepQueryKey
  >({
    queryKey: [GET_SHARED_STEP_KEY, projectKey, sharedStepKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/shared-steps/{key}", {
          params: { path: { project_key: projectKey, key: sharedStepKey } },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending: isEnabled && isPending, isError, isFetching, refetch };
};
