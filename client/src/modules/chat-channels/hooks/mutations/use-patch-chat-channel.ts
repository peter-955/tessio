"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { ChatChannelMutationOptions } from "../../typing/types/chat-channel-mutation-options.type";
import type { ChatChannelUpdate } from "../../typing/types/chat-channel-update.type";
import type { ChatChannel } from "../../typing/types/chat-channel.type";
import { GET_CHAT_CHANNELS_KEY } from "../queries/use-get-chat-channels";

type Options = ChatChannelMutationOptions<ChatChannel, ChatChannelUpdate>;

export const usePatchChatChannel = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<ChatChannel, ApiError, ChatChannelUpdate> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<ChatChannel, ChatChannelUpdate>({
    ...mutationOptions,
    mutationFn: ({ chatChannelId, body }) => {
      return unwrapResponse(
        apiClient.PATCH("/api/projects/{project_key}/chat-channels/{chat_channel_id}", {
          params: { path: { project_key: projectKey, chat_channel_id: chatChannelId } },
          body,
        }),
      );
    },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_CHAT_CHANNELS_KEY, projectKey] });

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
