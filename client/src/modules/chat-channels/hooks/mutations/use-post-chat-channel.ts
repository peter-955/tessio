"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { ChatChannelMutationOptions } from "../../typing/types/chat-channel-mutation-options.type";
import type { ChatChannel, CreateChatChannelRequest } from "../../typing/types/chat-channel.type";
import { GET_CHAT_CHANNELS_KEY } from "../queries/use-get-chat-channels";

type Options = ChatChannelMutationOptions<ChatChannel, CreateChatChannelRequest>;

export const usePostChatChannel = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<ChatChannel, ApiError, CreateChatChannelRequest> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<ChatChannel, CreateChatChannelRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/chat-channels", {
          params: { path: { project_key: projectKey } },
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
