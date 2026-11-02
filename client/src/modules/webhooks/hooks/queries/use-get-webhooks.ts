"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { Webhook } from "../../typing/types/webhook.type";

export const GET_WEBHOOKS_KEY = "GET_WEBHOOKS_KEY";

export type GetWebhooksQueryKey = [typeof GET_WEBHOOKS_KEY, string];

type Result = Pick<
  UseQueryResult<Webhook[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetWebhooks = (projectKey: string, isEnabled = true): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    Webhook[],
    GetWebhooksQueryKey
  >({
    queryKey: [GET_WEBHOOKS_KEY, projectKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/webhooks", {
          params: { path: { project_key: projectKey } },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
