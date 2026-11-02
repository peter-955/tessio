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
import { GET_STORY_KEY, type GetStoryQueryKey } from "../queries/use-get-story";

export const usePatchStory = (
  projectKey: string,
  jiraKey: string,
  options: StoryMutationOptions<StoryDetail, StoryRequest> = {},
): UseMutationResult<StoryDetail, ApiError, StoryRequest> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<StoryDetail, StoryRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.PATCH("/api/projects/{project_key}/stories/{jira_key}", {
          params: { path: { project_key: projectKey, jira_key: jiraKey } },
          body,
        }),
      );
    },
    onSuccess: async (story, variables, onMutateResult, context) => {
      const queryKey: GetStoryQueryKey = [GET_STORY_KEY, projectKey, jiraKey];
      queryClient.setQueryData(queryKey, story);
      await queryClient.invalidateQueries({ queryKey: [GET_STORIES_KEY] });

      return onSuccess?.(story, variables, onMutateResult, context);
    },
  });
};
