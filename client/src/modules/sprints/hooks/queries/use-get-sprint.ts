"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { Sprint } from "../../typing/types/sprint.type";

export const GET_SPRINT_KEY = "GET_SPRINT_KEY";

export type GetSprintQueryKey = [typeof GET_SPRINT_KEY, string, string];

type Result = Pick<
  UseQueryResult<Sprint, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetSprint = (projectKey: string, sprintId: string, isEnabled = true): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    Sprint,
    GetSprintQueryKey
  >({
    queryKey: [GET_SPRINT_KEY, projectKey, sprintId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/sprints/{sprint_id}", {
          params: { path: { project_key: projectKey, sprint_id: sprintId } },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
