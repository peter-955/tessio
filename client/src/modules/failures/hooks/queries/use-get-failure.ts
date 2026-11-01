"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { UUID_PATTERN } from "@/modules/sprints/typing/constants/sprint.constant";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { FailureDetail } from "../../typing/types/failure.type";

export const GET_FAILURE_KEY = "GET_FAILURE_KEY";

export type GetFailureQueryKey = [typeof GET_FAILURE_KEY, string, string];

type Result = Pick<
  UseQueryResult<FailureDetail, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetFailure = (projectKey: string, failureId: string): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    FailureDetail,
    GetFailureQueryKey
  >({
    queryKey: [GET_FAILURE_KEY, projectKey, failureId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/failures/{failure_id}", {
          params: { path: { project_key: projectKey, failure_id: failureId } },
          signal,
        }),
      );
    },
    enabled: UUID_PATTERN.test(failureId),
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
