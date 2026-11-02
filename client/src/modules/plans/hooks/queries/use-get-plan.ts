"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { UUID_PATTERN } from "@/modules/sprints/typing/constants/sprint.constant";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { PlanDetail } from "../../typing/types/plan.type";

export const GET_PLAN_KEY = "GET_PLAN_KEY";

export type GetPlanQueryKey = [typeof GET_PLAN_KEY, string, string];

type Result = Pick<
  UseQueryResult<PlanDetail, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetPlan = (projectKey: string, planId: string): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    PlanDetail,
    GetPlanQueryKey
  >({
    queryKey: [GET_PLAN_KEY, projectKey, planId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/plans/{plan_id}", {
          params: { path: { project_key: projectKey, plan_id: planId } },
          signal,
        }),
      );
    },
    enabled: UUID_PATTERN.test(planId),
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
