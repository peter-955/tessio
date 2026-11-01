"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { CreateApiTokenRequest, CreatedApiToken } from "../../typing/types/api-token.type";
import type { ConnectClaudeMutationOptions } from "../../typing/types/connect-claude-mutation-options.type";
import { GET_API_TOKENS_KEY } from "../queries/use-get-api-tokens";

type Options = ConnectClaudeMutationOptions<CreatedApiToken, CreateApiTokenRequest>;

export const usePostApiToken = (
  options: Options = {},
): UseMutationResult<CreatedApiToken, ApiError, CreateApiTokenRequest> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<CreatedApiToken, CreateApiTokenRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(apiClient.POST("/api/me/api-tokens", { body }));
    },
    gcTime: 0,
    isGlobalErrorToastDisabled: true,
    onSuccess: (createdToken, variables, onMutateResult, context) => {
      void queryClient.invalidateQueries({ queryKey: [GET_API_TOKENS_KEY] });

      return onSuccess?.(createdToken, variables, onMutateResult, context);
    },
  });
};
