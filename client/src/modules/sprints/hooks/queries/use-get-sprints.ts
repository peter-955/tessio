"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { Sprint } from "../../typing/types/sprint.type";

export const GET_SPRINTS_KEY = "GET_SPRINTS_KEY";

export type GetSprintsQueryKey = [typeof GET_SPRINTS_KEY, string];

type Result = Pick<
  UseQueryResult<Sprint[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetSprints = (projectKey: string): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    Sprint[],
    GetSprintsQueryKey
  >({
    queryKey: [GET_SPRINTS_KEY, projectKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/sprints", {
          params: { path: { project_key: projectKey } },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
