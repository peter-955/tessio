"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { UNAUTHORIZED_STATUS } from "../typing/constants/http-status.constant";
import { SignInReason } from "../typing/enums/sign-in-reason.enum";
import type { SignInStep } from "../typing/types/sign-in-step.type";
import { buildSignInPath, buildSignInStepPath } from "../utils/auth-path.util";
import { useGetCurrentUser } from "./queries/use-get-current-user";
import { useAuthSearchParams } from "./use-auth-search-params";

interface Options {
  isEnabled?: boolean;
}

interface Result {
  isReady: boolean;
  isLoadFailed: boolean;
  isRetrying: boolean;
  retry: () => void;
}

export const useSignInStepRedirect = (
  expectedStep: SignInStep,
  { isEnabled = true }: Options = {},
): Result => {
  const router = useRouter();
  const { nextPath } = useAuthSearchParams();
  const { data: currentUser, error, refetch, isRefetching } = useGetCurrentUser();
  const isUnauthorized = error?.status === UNAUTHORIZED_STATUS;
  const currentStep = currentUser?.nextStep;

  useEffect(() => {
    if (!isEnabled) {
      return;
    }
    if (isUnauthorized) {
      router.replace(buildSignInPath({ nextPath, reason: SignInReason.EXPIRED }));
      return;
    }
    if (currentStep !== undefined && currentStep !== expectedStep) {
      router.replace(buildSignInStepPath(currentStep, nextPath));
    }
  }, [currentStep, expectedStep, isEnabled, isUnauthorized, nextPath, router]);

  const retry = (): void => {
    void refetch();
  };

  return {
    isReady: currentStep === expectedStep,
    isLoadFailed: error !== null && !isUnauthorized && currentUser === undefined,
    isRetrying: isRefetching,
    retry,
  };
};
