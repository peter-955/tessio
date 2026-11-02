"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { WebhookMutationOptions } from "../../typing/types/webhook-mutation-options.type";
import type { CreateWebhookRequest, WebhookWithSecret } from "../../typing/types/webhook.type";
import { GET_WEBHOOKS_KEY } from "../queries/use-get-webhooks";

type Options = WebhookMutationOptions<WebhookWithSecret, CreateWebhookRequest>;

export const usePostWebhook = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<WebhookWithSecret, ApiError, CreateWebhookRequest> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<WebhookWithSecret, CreateWebhookRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/webhooks", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
    gcTime: 0,
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_WEBHOOKS_KEY, projectKey] });

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
