"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { SharedStepMutationOptions } from "../../typing/types/shared-step-mutation-options.type";
import type { CreateSharedStepRequest, SharedStep } from "../../typing/types/shared-step.type";
import { useSharedStepApiErrors } from "../use-shared-step-api-errors";
import { useStoreSharedStep } from "../use-shared-step-cache";

type Options = SharedStepMutationOptions<SharedStep, CreateSharedStepRequest>;

export const usePostSharedStep = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<SharedStep, ApiError, CreateSharedStepRequest> => {
  const storeSharedStep = useStoreSharedStep(projectKey);
  const apiErrors = useSharedStepApiErrors();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<SharedStep, CreateSharedStepRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/shared-steps", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
    apiErrors,
    onSuccess: async (sharedStep, variables, onMutateResult, context) => {
      await storeSharedStep(sharedStep);

      return onSuccess?.(sharedStep, variables, onMutateResult, context);
    },
  });
};
