"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import { GET_NOTIFICATIONS_KEY } from "./queries/use-get-notifications";
import { GET_UNREAD_NOTIFICATION_COUNT_KEY } from "./queries/use-get-unread-notification-count";

export const useInvalidateNotifications = (): (() => void) => {
  const queryClient = useQueryClient();

  return useCallback((): void => {
    void queryClient.invalidateQueries({ queryKey: [GET_NOTIFICATIONS_KEY] });
    void queryClient.invalidateQueries({ queryKey: [GET_UNREAD_NOTIFICATION_COUNT_KEY] });
  }, [queryClient]);
};
