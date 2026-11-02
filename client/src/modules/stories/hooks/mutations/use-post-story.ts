"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { StoryRequest } from "../../typing/types/story-editor.type";
import type { StoryMutationOptions } from "../../typing/types/story-mutation-options.type";
import type { StoryDetail } from "../../typing/types/story.type";
import { GET_STORIES_KEY } from "../queries/use-get-stories";

export const usePostStory = (
  projectKey: string,
  options: StoryMutationOptions<StoryDetail, StoryRequest> = {},
): UseMutationResult<StoryDetail, ApiError, StoryRequest> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<StoryDetail, StoryRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/stories", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
    onSuccess: async (story, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_STORIES_KEY] });

      return onSuccess?.(story, variables, onMutateResult, context);
    },
  });
};
