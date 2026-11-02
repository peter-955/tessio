"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { ChatChannelMutationOptions } from "../../typing/types/chat-channel-mutation-options.type";
import { GET_CHAT_CHANNELS_KEY } from "../queries/use-get-chat-channels";

type Options = ChatChannelMutationOptions<void, string>;

export const useDeleteChatChannel = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<void, ApiError, string> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<void, string>({
    ...mutationOptions,
    mutationFn: (chatChannelId) => {
      return unwrapResponse(
        apiClient.DELETE("/api/projects/{project_key}/chat-channels/{chat_channel_id}", {
          params: { path: { project_key: projectKey, chat_channel_id: chatChannelId } },
        }),
      );
    },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_CHAT_CHANNELS_KEY, projectKey] });

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
