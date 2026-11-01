"use client";

import type { Project } from "@/components/project-context/typing/types/project.type";
import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { skipToken, type UseQueryResult } from "@tanstack/react-query";

export const GET_PROJECT_KEY = "GET_PROJECT_KEY";

export type GetProjectQueryKey = [typeof GET_PROJECT_KEY, string | null];

type Result = Pick<
  UseQueryResult<Project, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetProject = (projectKey: string | null): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    Project,
    GetProjectQueryKey
  >({
    queryKey: [GET_PROJECT_KEY, projectKey],
    queryFn:
      projectKey === null
        ? skipToken
        : () => {
            return unwrapResponse(
              apiClient.GET("/api/projects/{project_key}", {
                params: { path: { project_key: projectKey } },
              }),
            );
          },
    enabled: projectKey !== null,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
