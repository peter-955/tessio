"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { NotificationPreference } from "../../typing/types/notification-preference.type";

export const GET_NOTIFICATION_PREFERENCES_KEY = "GET_NOTIFICATION_PREFERENCES_KEY";

export type GetNotificationPreferencesQueryKey = [typeof GET_NOTIFICATION_PREFERENCES_KEY];

type Result = Pick<
  UseQueryResult<NotificationPreference[], ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetNotificationPreferences = (): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    NotificationPreference[],
    GetNotificationPreferencesQueryKey
  >({
    queryKey: [GET_NOTIFICATION_PREFERENCES_KEY],
    queryFn: ({ signal }) => {
      return unwrapResponse(apiClient.GET("/api/me/notification-preferences", { signal }));
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError, isFetching, refetch };
};
