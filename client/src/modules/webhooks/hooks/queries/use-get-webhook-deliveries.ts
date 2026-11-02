"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { WEBHOOK_DELIVERY_LIST_LIMIT } from "../../typing/constants/webhook.constant";
import type { WebhookDelivery } from "../../typing/types/webhook.type";

export const GET_WEBHOOK_DELIVERIES_KEY = "GET_WEBHOOK_DELIVERIES_KEY";

export type GetWebhookDeliveriesQueryKey = [typeof GET_WEBHOOK_DELIVERIES_KEY, string, string];

type Result = Pick<
  UseQueryResult<WebhookDelivery[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetWebhookDeliveries = (
  projectKey: string,
  webhookId: string,
  isEnabled = true,
): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    WebhookDelivery[],
    GetWebhookDeliveriesQueryKey
  >({
    queryKey: [GET_WEBHOOK_DELIVERIES_KEY, projectKey, webhookId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/webhooks/{webhook_id}/deliveries", {
          params: {
            path: { project_key: projectKey, webhook_id: webhookId },
            query: { limit: WEBHOOK_DELIVERY_LIST_LIMIT },
          },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
