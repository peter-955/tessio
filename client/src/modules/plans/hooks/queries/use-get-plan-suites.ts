"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { PlanSuiteSummary } from "../../typing/types/plan.type";

export const GET_PLAN_SUITES_KEY = "GET_PLAN_SUITES_KEY";

export type GetPlanSuitesQueryKey = [typeof GET_PLAN_SUITES_KEY, string];

type Result = Pick<
  UseQueryResult<PlanSuiteSummary[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetPlanSuites = (projectKey: string): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    PlanSuiteSummary[],
    GetPlanSuitesQueryKey
  >({
    queryKey: [GET_PLAN_SUITES_KEY, projectKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/suites", {
          params: { path: { project_key: projectKey }, query: { archived: false } },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
