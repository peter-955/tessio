"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { PlanMutationOptions } from "../../typing/types/plan-mutation-options.type";
import type { PlanDetail } from "../../typing/types/plan.type";
import { useInvalidatePlans } from "../use-invalidate-plans";
import { usePlanApiErrors } from "../use-plan-api-errors";

export const usePostPlanClose = (
  projectKey: string,
  planId: string,
  options: PlanMutationOptions<PlanDetail, void> = {},
): UseMutationResult<PlanDetail, ApiError, void> => {
  const invalidatePlans = useInvalidatePlans();
  const apiErrors = usePlanApiErrors();

  return useAppMutation<PlanDetail>({
    ...options,
    mutationFn: () => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/plans/{plan_id}/close", {
          params: { path: { project_key: projectKey, plan_id: planId } },
        }),
      );
    },
    apiErrors,
    onSettled: () => {
      return invalidatePlans();
    },
  });
};
