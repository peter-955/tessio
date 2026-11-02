"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { ChatChannel } from "../../typing/types/chat-channel.type";

export const GET_CHAT_CHANNELS_KEY = "GET_CHAT_CHANNELS_KEY";

export type GetChatChannelsQueryKey = [typeof GET_CHAT_CHANNELS_KEY, string];

type Result = Pick<
  UseQueryResult<ChatChannel[], ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetChatChannels = (projectKey: string): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    ChatChannel[],
    GetChatChannelsQueryKey
  >({
    queryKey: [GET_CHAT_CHANNELS_KEY, projectKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/chat-channels", {
          params: { path: { project_key: projectKey } },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError, isFetching, refetch };
};
