"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { ConnectClaudeMutationOptions } from "../../typing/types/connect-claude-mutation-options.type";
import { GET_API_TOKENS_KEY } from "../queries/use-get-api-tokens";

type Options = ConnectClaudeMutationOptions<void, string>;

export const useDeleteApiToken = (
  options: Options = {},
): UseMutationResult<void, ApiError, string> => {
  const { t } = useTranslation("connectClaude");
  const queryClient = useQueryClient();
  const { showSuccessToast } = useShowToast();
  const { onSuccess, onError, ...mutationOptions } = options;

  const refreshTokens = (): void => {
    void queryClient.invalidateQueries({ queryKey: [GET_API_TOKENS_KEY] });
  };

  return useAppMutation<void, string>({
    ...mutationOptions,
    mutationFn: (tokenId) => {
      return unwrapResponse(
        apiClient.DELETE("/api/me/api-tokens/{token_id}", {
          params: { path: { token_id: tokenId } },
        }),
      );
    },
    onSuccess: (data, tokenId, onMutateResult, context) => {
      refreshTokens();
      showSuccessToast(t("revoke.done"));

      return onSuccess?.(data, tokenId, onMutateResult, context);
    },
    onError: (error, tokenId, onMutateResult, context) => {
      if (error.code === "NOT_FOUND") {
        refreshTokens();
      }

      return onError?.(error, tokenId, onMutateResult, context);
    },
  });
};
