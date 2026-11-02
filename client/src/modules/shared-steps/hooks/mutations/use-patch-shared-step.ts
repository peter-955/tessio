"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { SharedStepMutationOptions } from "../../typing/types/shared-step-mutation-options.type";
import type { SharedStepUpdateVariables } from "../../typing/types/shared-step-update-variables.type";
import type { SharedStep } from "../../typing/types/shared-step.type";
import { useSharedStepApiErrors } from "../use-shared-step-api-errors";
import { useStoreSharedStep } from "../use-shared-step-cache";

type Options = SharedStepMutationOptions<SharedStep, SharedStepUpdateVariables>;

export const usePatchSharedStep = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<SharedStep, ApiError, SharedStepUpdateVariables> => {
  const storeSharedStep = useStoreSharedStep(projectKey);
  const apiErrors = useSharedStepApiErrors();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<SharedStep, SharedStepUpdateVariables>({
    ...mutationOptions,
    mutationFn: ({ key, body }) => {
      return unwrapResponse(
        apiClient.PATCH("/api/projects/{project_key}/shared-steps/{key}", {
          params: { path: { project_key: projectKey, key } },
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
