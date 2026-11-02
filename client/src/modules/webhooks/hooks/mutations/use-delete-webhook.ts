"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { WebhookMutationOptions } from "../../typing/types/webhook-mutation-options.type";
import { GET_WEBHOOK_DELIVERIES_KEY } from "../queries/use-get-webhook-deliveries";
import { GET_WEBHOOKS_KEY } from "../queries/use-get-webhooks";

type Options = WebhookMutationOptions<void, string>;

export const useDeleteWebhook = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<void, ApiError, string> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<void, string>({
    ...mutationOptions,
    mutationFn: (webhookId) => {
      return unwrapResponse(
        apiClient.DELETE("/api/projects/{project_key}/webhooks/{webhook_id}", {
          params: { path: { project_key: projectKey, webhook_id: webhookId } },
        }),
      );
    },
    onSuccess: async (data, webhookId, onMutateResult, context) => {
      queryClient.removeQueries({
        queryKey: [GET_WEBHOOK_DELIVERIES_KEY, projectKey, webhookId],
      });
      await queryClient.invalidateQueries({ queryKey: [GET_WEBHOOKS_KEY, projectKey] });

      return onSuccess?.(data, webhookId, onMutateResult, context);
    },
  });
};
