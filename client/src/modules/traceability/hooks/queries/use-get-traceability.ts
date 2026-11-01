"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { Traceability } from "../../typing/types/traceability.type";

export const GET_TRACEABILITY_KEY = "GET_TRACEABILITY_KEY";

export type GetTraceabilityQueryKey = [typeof GET_TRACEABILITY_KEY, string, string];

type Result = Pick<
  UseQueryResult<Traceability, ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetTraceability = (projectKey: string, jiraKey: string): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    Traceability,
    GetTraceabilityQueryKey
  >({
    queryKey: [GET_TRACEABILITY_KEY, projectKey, jiraKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/stories/{jira_key}/traceability", {
          params: { path: { project_key: projectKey, jira_key: jiraKey } },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError, isFetching, refetch };
};
