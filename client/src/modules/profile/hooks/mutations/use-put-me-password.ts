"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { ChangePasswordRequest } from "../../typing/types/profile-api.type";
import type { ProfileMutationOptions } from "../../typing/types/profile-mutation-options.type";

type Options = ProfileMutationOptions<void, ChangePasswordRequest>;

export const usePutMePassword = (
  options: Options = {},
): UseMutationResult<void, ApiError, ChangePasswordRequest> => {
  return useAppMutation<void, ChangePasswordRequest>({
    ...options,
    mutationFn: (body) => {
      return unwrapResponse(apiClient.PUT("/api/me/password", { body }));
    },
    isGlobalErrorToastDisabled: true,
  });
};
