"use client";

import { apiClient } from "@/lib/api/api-client";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UnreadNotificationCount } from "../../typing/types/notification.type";

export const GET_UNREAD_NOTIFICATION_COUNT_KEY = "GET_UNREAD_NOTIFICATION_COUNT_KEY";

export type GetUnreadNotificationCountQueryKey = [typeof GET_UNREAD_NOTIFICATION_COUNT_KEY];

interface Result {
  unreadCount: number;
  isError: boolean;
}

export const useGetUnreadNotificationCount = (): Result => {
  const { data, isError } = useAppQuery<
    UnreadNotificationCount,
    GetUnreadNotificationCountQueryKey
  >({
    queryKey: [GET_UNREAD_NOTIFICATION_COUNT_KEY],
    queryFn: ({ signal }) => {
      return unwrapResponse(apiClient.GET("/api/notifications/unread-count", { signal }));
    },
    isGlobalErrorToastDisabled: true,
  });

  return { unreadCount: data?.count ?? 0, isError };
};
