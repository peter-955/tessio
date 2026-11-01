"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { RecoveryCodesResponse, TwoFactorCodeRequest } from "../../typing/types/auth-api.type";
import type { AuthMutationOptions } from "../../typing/types/auth-mutation-options.type";

type Options = AuthMutationOptions<RecoveryCodesResponse, TwoFactorCodeRequest>;

export const usePostTwoFactorConfirm = (
  options: Options = {},
): UseMutationResult<RecoveryCodesResponse, ApiError, TwoFactorCodeRequest> => {
  return useAppMutation<RecoveryCodesResponse, TwoFactorCodeRequest>({
    ...options,
    mutationFn: (body) => {
      return unwrapResponse(apiClient.POST("/api/auth/two-factor/confirm", { body }));
    },
    isGlobalErrorToastDisabled: true,
  });
};
