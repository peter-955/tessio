"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { SIGN_IN_PATH } from "@/modules/auth/typing/constants/auth-route.constant";
import { UNAUTHORIZED_STATUS } from "@/modules/auth/typing/constants/http-status.constant";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import type { ProfileMutationOptions } from "../../typing/types/profile-mutation-options.type";

type Options = ProfileMutationOptions<void, void>;

export const usePostSignOutAll = (
  options: Options = {},
): UseMutationResult<void, ApiError, void> => {
  const queryClient = useQueryClient();
  const router = useRouter();
  const { onSuccess, onError, ...mutationOptions } = options;

  const leaveSession = (): void => {
    queryClient.clear();
    router.replace(SIGN_IN_PATH);
  };

  return useAppMutation<void, void>({
    ...mutationOptions,
    mutationFn: () => {
      return unwrapResponse(apiClient.POST("/api/auth/sign-out-all"));
    },
    onSuccess: (data, variables, onMutateResult, context) => {
      leaveSession();

      return onSuccess?.(data, variables, onMutateResult, context);
    },
    onError: (error, variables, onMutateResult, context) => {
      if (error.status === UNAUTHORIZED_STATUS) {
        leaveSession();
      }

      return onError?.(error, variables, onMutateResult, context);
    },
  });
};
