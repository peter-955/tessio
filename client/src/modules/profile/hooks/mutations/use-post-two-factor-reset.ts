"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_CURRENT_USER_KEY } from "@/modules/auth/hooks/queries/use-get-current-user";
import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import { buildSignInStepPath } from "@/modules/auth/utils/auth-path.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { PROFILE_PATH } from "../../typing/constants/profile.constant";
import type {
  PasswordConfirmationRequest,
  TwoFactorResetResponse,
} from "../../typing/types/profile-api.type";
import type { ProfileMutationOptions } from "../../typing/types/profile-mutation-options.type";

type Options = ProfileMutationOptions<TwoFactorResetResponse, PasswordConfirmationRequest>;

export const usePostTwoFactorReset = (
  options: Options = {},
): UseMutationResult<TwoFactorResetResponse, ApiError, PasswordConfirmationRequest> => {
  const queryClient = useQueryClient();
  const router = useRouter();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<TwoFactorResetResponse, PasswordConfirmationRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(apiClient.POST("/api/me/two-factor/reset", { body }));
    },
    isGlobalErrorToastDisabled: true,
    onSuccess: (response, variables, onMutateResult, context) => {
      queryClient.setQueryData<CurrentUser>([GET_CURRENT_USER_KEY], (user) => {
        if (user === undefined) {
          return user;
        }

        return { ...user, nextStep: response.nextStep, isTwoFactorSetUp: false };
      });
      router.replace(buildSignInStepPath(response.nextStep, PROFILE_PATH));

      return onSuccess?.(response, variables, onMutateResult, context);
    },
  });
};
