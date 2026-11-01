"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { AcceptInviteVariables, SignInResponse } from "../../typing/types/auth-api.type";
import type { AuthMutationOptions } from "../../typing/types/auth-mutation-options.type";
import { GET_CURRENT_USER_KEY } from "../queries/use-get-current-user";

type Options = AuthMutationOptions<SignInResponse, AcceptInviteVariables>;

export const usePostAcceptInvite = (
  options: Options = {},
): UseMutationResult<SignInResponse, ApiError, AcceptInviteVariables> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<SignInResponse, AcceptInviteVariables>({
    ...mutationOptions,
    mutationFn: ({ token, password }) => {
      return unwrapResponse(
        apiClient.POST("/api/auth/invites/{token}", {
          params: { path: { token } },
          body: { password },
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.removeQueries({ queryKey: [GET_CURRENT_USER_KEY] });

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
