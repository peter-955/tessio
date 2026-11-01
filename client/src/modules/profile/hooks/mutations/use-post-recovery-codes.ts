"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { PasswordConfirmationRequest } from "../../typing/types/profile-api.type";
import type { ProfileMutationOptions } from "../../typing/types/profile-mutation-options.type";

type Options = ProfileMutationOptions<string[], PasswordConfirmationRequest>;

export const usePostRecoveryCodes = (
  options: Options = {},
): UseMutationResult<string[], ApiError, PasswordConfirmationRequest> => {
  return useAppMutation<string[], PasswordConfirmationRequest>({
    ...options,
    mutationFn: async (body) => {
      const response = await unwrapResponse(apiClient.POST("/api/me/recovery-codes", { body }));

      return response.recoveryCodes;
    },
    gcTime: 0,
    isGlobalErrorToastDisabled: true,
  });
};
