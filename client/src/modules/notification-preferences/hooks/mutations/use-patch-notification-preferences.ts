"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { NotificationPreferenceMutationOptions } from "../../typing/types/notification-preference-mutation-options.type";
import type {
  NotificationPreference,
  UpdateNotificationPreferencesRequest,
} from "../../typing/types/notification-preference.type";
import {
  GET_NOTIFICATION_PREFERENCES_KEY,
  type GetNotificationPreferencesQueryKey,
} from "../queries/use-get-notification-preferences";

type Options = NotificationPreferenceMutationOptions<
  NotificationPreference[],
  UpdateNotificationPreferencesRequest
>;

export const usePatchNotificationPreferences = (
  options: Options = {},
): UseMutationResult<NotificationPreference[], ApiError, UpdateNotificationPreferencesRequest> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<NotificationPreference[], UpdateNotificationPreferencesRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(apiClient.PATCH("/api/me/notification-preferences", { body }));
    },
    onSuccess: (data, variables, onMutateResult, context) => {
      const queryKey: GetNotificationPreferencesQueryKey = [GET_NOTIFICATION_PREFERENCES_KEY];
      queryClient.setQueryData(queryKey, data);

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
