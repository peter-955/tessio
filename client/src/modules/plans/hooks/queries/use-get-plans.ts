"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { keepPreviousData, type UseQueryResult } from "@tanstack/react-query";
import type { PlanStatusFilter } from "../../typing/types/plan-status-filter.type";
import type { PlanSummary } from "../../typing/types/plan.type";

export const GET_PLANS_KEY = "GET_PLANS_KEY";

export type GetPlansQueryKey = [typeof GET_PLANS_KEY, string, PlanStatusFilter];

type Result = Pick<
  UseQueryResult<PlanSummary[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetPlans = (projectKey: string, status: PlanStatusFilter): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    PlanSummary[],
    GetPlansQueryKey
  >({
    queryKey: [GET_PLANS_KEY, projectKey, status],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/plans", {
          params: {
            path: { project_key: projectKey },
            query: status === "all" ? {} : { status },
          },
          signal,
        }),
      );
    },
    placeholderData: keepPreviousData,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
