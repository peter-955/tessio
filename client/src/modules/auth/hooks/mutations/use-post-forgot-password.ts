"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { ForgotPasswordRequest } from "../../typing/types/auth-api.type";
import type { AuthMutationOptions } from "../../typing/types/auth-mutation-options.type";

type Options = AuthMutationOptions<void, ForgotPasswordRequest>;

export const usePostForgotPassword = (
  options: Options = {},
): UseMutationResult<void, ApiError, ForgotPasswordRequest> => {
  return useAppMutation<void, ForgotPasswordRequest>({
    ...options,
    mutationFn: (body) => {
      return unwrapResponse(apiClient.POST("/api/auth/password/forgot", { body }));
    },
    isGlobalErrorToastDisabled: true,
  });
};
