"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { SignInRequest, SignInResponse } from "../../typing/types/auth-api.type";
import type { AuthMutationOptions } from "../../typing/types/auth-mutation-options.type";
import { GET_CURRENT_USER_KEY } from "../queries/use-get-current-user";

type Options = AuthMutationOptions<SignInResponse, SignInRequest>;

export const usePostSignIn = (
  options: Options = {},
): UseMutationResult<SignInResponse, ApiError, SignInRequest> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<SignInResponse, SignInRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(apiClient.POST("/api/auth/sign-in", { body }));
    },
    isGlobalErrorToastDisabled: true,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.removeQueries({ queryKey: [GET_CURRENT_USER_KEY] });

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
