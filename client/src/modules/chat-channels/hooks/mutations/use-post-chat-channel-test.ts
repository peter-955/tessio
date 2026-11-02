"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { ChatChannelMutationOptions } from "../../typing/types/chat-channel-mutation-options.type";
import type { ChatChannel } from "../../typing/types/chat-channel.type";
import { GET_CHAT_CHANNELS_KEY } from "../queries/use-get-chat-channels";

type Options = ChatChannelMutationOptions<ChatChannel, string>;

export const usePostChatChannelTest = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<ChatChannel, ApiError, string> => {
  const queryClient = useQueryClient();
  const { onSettled, ...mutationOptions } = options;

  return useAppMutation<ChatChannel, string>({
    ...mutationOptions,
    mutationFn: (chatChannelId) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/chat-channels/{chat_channel_id}/test", {
          params: { path: { project_key: projectKey, chat_channel_id: chatChannelId } },
        }),
      );
    },
    onSettled: async (data, error, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_CHAT_CHANNELS_KEY, projectKey] });

      return onSettled?.(data, error, variables, onMutateResult, context);
    },
  });
};
