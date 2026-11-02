"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { WebhookMutationOptions } from "../../typing/types/webhook-mutation-options.type";
import type { WebhookUpdate } from "../../typing/types/webhook-update.type";
import type { WebhookWithSecret } from "../../typing/types/webhook.type";
import { GET_WEBHOOKS_KEY } from "../queries/use-get-webhooks";

type Options = WebhookMutationOptions<WebhookWithSecret, WebhookUpdate>;

export const usePatchWebhook = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<WebhookWithSecret, ApiError, WebhookUpdate> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<WebhookWithSecret, WebhookUpdate>({
    ...mutationOptions,
    mutationFn: ({ webhookId, body }) => {
      return unwrapResponse(
        apiClient.PATCH("/api/projects/{project_key}/webhooks/{webhook_id}", {
          params: { path: { project_key: projectKey, webhook_id: webhookId } },
          body: { rotateSecret: false, ...body },
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
