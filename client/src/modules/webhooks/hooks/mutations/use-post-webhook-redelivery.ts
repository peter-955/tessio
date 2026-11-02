"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { WebhookMutationOptions } from "../../typing/types/webhook-mutation-options.type";
import type { WebhookRedelivery } from "../../typing/types/webhook-redelivery.type";
import type { WebhookDelivery } from "../../typing/types/webhook.type";
import { GET_WEBHOOK_DELIVERIES_KEY } from "../queries/use-get-webhook-deliveries";
import { GET_WEBHOOKS_KEY } from "../queries/use-get-webhooks";

type Options = WebhookMutationOptions<WebhookDelivery, WebhookRedelivery>;

export const usePostWebhookRedelivery = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<WebhookDelivery, ApiError, WebhookRedelivery> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<WebhookDelivery, WebhookRedelivery>({
    ...mutationOptions,
    mutationFn: ({ webhookId, deliveryId }) => {
      return unwrapResponse(
        apiClient.POST(
          "/api/projects/{project_key}/webhooks/{webhook_id}/redeliver/{delivery_id}",
          {
            params: {
              path: { project_key: projectKey, webhook_id: webhookId, delivery_id: deliveryId },
            },
          },
        ),
      );
    },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: [GET_WEBHOOK_DELIVERIES_KEY, projectKey, variables.webhookId],
        }),
        queryClient.invalidateQueries({ queryKey: [GET_WEBHOOKS_KEY, projectKey] }),
      ]);

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
