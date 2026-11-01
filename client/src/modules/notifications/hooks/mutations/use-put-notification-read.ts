"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { UseMutationResult } from "@tanstack/react-query";
import { useInvalidateNotifications } from "../use-invalidate-notifications";

export const usePutNotificationRead = (): UseMutationResult<void, ApiError, string> => {
  const invalidateNotifications = useInvalidateNotifications();
  const { showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();

  return useAppMutation<void, string>({
    mutationFn: async (notificationId) => {
      await unwrapResponse(
        apiClient.PUT("/api/notifications/{notification_id}/read", {
          params: { path: { notification_id: notificationId } },
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
    onError: (error) => {
      if (error.code !== "NOT_FOUND") {
        showErrorToast(resolveMessage(error));
      }
    },
    onSettled: () => {
      invalidateNotifications();
    },
  });
};
