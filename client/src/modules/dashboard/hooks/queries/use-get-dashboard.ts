"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { DashboardSummary } from "../../typing/types/dashboard.type";

export const GET_DASHBOARD_KEY = "GET_DASHBOARD_KEY";

export type GetDashboardQueryKey = [typeof GET_DASHBOARD_KEY, string, string | null];

type Result = Pick<
  UseQueryResult<DashboardSummary, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetDashboard = (projectKey: string, sprintId: string | null): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    DashboardSummary,
    GetDashboardQueryKey
  >({
    queryKey: [GET_DASHBOARD_KEY, projectKey, sprintId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/dashboard", {
          params: {
            path: { project_key: projectKey },
            ...(sprintId === null ? {} : { query: { sprintId } }),
          },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
