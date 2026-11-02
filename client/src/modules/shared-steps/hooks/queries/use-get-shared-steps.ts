"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { keepPreviousData, type UseQueryResult } from "@tanstack/react-query";
import type { SharedStep } from "../../typing/types/shared-step.type";

export const GET_SHARED_STEPS_KEY = "GET_SHARED_STEPS_KEY";

export type GetSharedStepsQueryKey = [typeof GET_SHARED_STEPS_KEY, string, boolean];

type Result = Pick<
  UseQueryResult<SharedStep[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetSharedSteps = (
  projectKey: string,
  isArchivedIncluded = false,
  isEnabled = true,
): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    SharedStep[],
    GetSharedStepsQueryKey
  >({
    queryKey: [GET_SHARED_STEPS_KEY, projectKey, isArchivedIncluded],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/shared-steps", {
          params: {
            path: { project_key: projectKey },
            query: isArchivedIncluded ? { archived: true } : {},
          },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    placeholderData: keepPreviousData,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
