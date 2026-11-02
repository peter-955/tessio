"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import type { SharedStep } from "../typing/types/shared-step.type";
import { GET_SHARED_STEP_KEY, type GetSharedStepQueryKey } from "./queries/use-get-shared-step";
import { GET_SHARED_STEPS_KEY } from "./queries/use-get-shared-steps";

export const useStoreSharedStep = (
  projectKey: string,
): ((sharedStep: SharedStep) => Promise<void>) => {
  const queryClient = useQueryClient();

  return useCallback(
    async (sharedStep: SharedStep): Promise<void> => {
      const queryKey: GetSharedStepQueryKey = [GET_SHARED_STEP_KEY, projectKey, sharedStep.key];
      queryClient.setQueryData<SharedStep>(queryKey, sharedStep);
      await queryClient.invalidateQueries({ queryKey: [GET_SHARED_STEPS_KEY, projectKey] });
    },
    [projectKey, queryClient],
  );
};
