"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import {
  useInfiniteQuery,
  type InfiniteData,
  type UseInfiniteQueryResult,
} from "@tanstack/react-query";
import { useMemo } from "react";
import { NOTIFICATION_PAGE_SIZE } from "../../typing/constants/notification.constant";
import type { Notification, NotificationPage } from "../../typing/types/notification.type";

export const GET_NOTIFICATIONS_KEY = "GET_NOTIFICATIONS_KEY";

export type GetNotificationsQueryKey = [typeof GET_NOTIFICATIONS_KEY, { isUnreadOnly: boolean }];

type NotificationCursor = string | null;

type QueryResult = UseInfiniteQueryResult<
  InfiniteData<NotificationPage, NotificationCursor>,
  ApiError
>;

interface Options {
  isUnreadOnly: boolean;
  isEnabled: boolean;
}

interface Result extends Pick<
  QueryResult,
  "isPending" | "isError" | "refetch" | "isRefetching" | "hasNextPage" | "fetchNextPage"
> {
  notifications: Notification[];
  isFetchingNextPage: boolean;
}

export const useGetNotifications = ({ isUnreadOnly, isEnabled }: Options): Result => {
  const {
    data,
    isPending,
    isError,
    refetch,
    isRefetching,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery<
    NotificationPage,
    ApiError,
    InfiniteData<NotificationPage, NotificationCursor>,
    GetNotificationsQueryKey,
    NotificationCursor
  >({
    queryKey: [GET_NOTIFICATIONS_KEY, { isUnreadOnly }],
    queryFn: ({ pageParam, signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/notifications", {
          params: {
            query: { unreadOnly: isUnreadOnly, cursor: pageParam, limit: NOTIFICATION_PAGE_SIZE },
          },
          signal,
        }),
      );
    },
    initialPageParam: null as NotificationCursor,
    getNextPageParam: (page) => {
      return page.nextCursor;
    },
    enabled: isEnabled,
  });

  const notifications = useMemo((): Notification[] => {
    return (
      data?.pages.flatMap((page) => {
        return page.items;
      }) ?? []
    );
  }, [data]);

  return {
    notifications,
    isPending,
    isError,
    refetch,
    isRefetching,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  };
};
