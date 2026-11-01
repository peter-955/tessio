"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import type { components } from "@/lib/api/openapi.type";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";

export const GET_ENVIRONMENTS_KEY = "GET_ENVIRONMENTS_KEY";

export type GetEnvironmentsQueryKey = [typeof GET_ENVIRONMENTS_KEY, string, boolean];

type EnvironmentResponse = components["schemas"]["EnvironmentResponse"];

interface Options {
  isIncludingArchived?: boolean;
}

type Result = Pick<
  UseQueryResult<EnvironmentResponse[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetEnvironments = (
  projectKey: string,
  { isIncludingArchived = false }: Options = {},
): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    EnvironmentResponse[],
    GetEnvironmentsQueryKey
  >({
    queryKey: [GET_ENVIRONMENTS_KEY, projectKey, isIncludingArchived],
    queryFn: () => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/environments", {
          params: {
            path: { project_key: projectKey },
            query: { includeArchived: isIncludingArchived },
          },
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
