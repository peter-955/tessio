"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import { useInvalidateNotifications } from "../use-invalidate-notifications";

export const usePutAllNotificationsRead = (): UseMutationResult<void, ApiError, void> => {
  const invalidateNotifications = useInvalidateNotifications();

  return useAppMutation<void>({
    mutationFn: async () => {
      await unwrapResponse(apiClient.PUT("/api/notifications/read-all"));
    },
    onSuccess: () => {
      invalidateNotifications();
    },
  });
};
