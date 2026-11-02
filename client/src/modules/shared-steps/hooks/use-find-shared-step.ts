"use client";

import type { SharedStepLookup } from "../typing/types/shared-step-lookup.type";
import { useGetSharedSteps } from "./queries/use-get-shared-steps";

export const useFindSharedStep = (projectKey: string, sharedStepKey: string): SharedStepLookup => {
  const { data, isPending, isError } = useGetSharedSteps(projectKey, true);
  const normalizedKey = sharedStepKey.toLowerCase();

  return {
    sharedStep: data?.find((sharedStep) => sharedStep.key === normalizedKey) ?? null,
    isPending,
    isError,
  };
};
