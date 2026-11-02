"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { PlanMutationOptions } from "../../typing/types/plan-mutation-options.type";
import type { CreatePlanRequest, PlanDetail } from "../../typing/types/plan.type";
import { useInvalidatePlans } from "../use-invalidate-plans";
import { usePlanApiErrors } from "../use-plan-api-errors";

export const usePostPlan = (
  projectKey: string,
  options: PlanMutationOptions<PlanDetail, CreatePlanRequest> = {},
): UseMutationResult<PlanDetail, ApiError, CreatePlanRequest> => {
  const invalidatePlans = useInvalidatePlans();
  const apiErrors = usePlanApiErrors();

  return useAppMutation<PlanDetail, CreatePlanRequest>({
    ...options,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/plans", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
    apiErrors,
    onSettled: () => {
      return invalidatePlans();
    },
  });
};
