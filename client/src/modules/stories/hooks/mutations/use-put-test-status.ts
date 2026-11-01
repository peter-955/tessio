"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { StoryMutationOptions } from "../../typing/types/story-mutation-options.type";
import type { StoryDetail, TestStatus } from "../../typing/types/story.type";
import { GET_STORIES_KEY } from "../queries/use-get-stories";
import { GET_STORY_KEY, type GetStoryQueryKey } from "../queries/use-get-story";

type Options = StoryMutationOptions<StoryDetail, TestStatus>;

export const usePutTestStatus = (
  projectKey: string,
  jiraKey: string,
  options: Options = {},
): UseMutationResult<StoryDetail, ApiError, TestStatus> => {
  const queryClient = useQueryClient();
  const { t } = useTranslation("stories");
  const { onSuccess, onError, ...mutationOptions } = options;

  return useAppMutation<StoryDetail, TestStatus>({
    ...mutationOptions,
    mutationFn: (testStatus) => {
      return unwrapResponse(
        apiClient.PUT("/api/projects/{project_key}/stories/{jira_key}/test-status", {
          params: { path: { project_key: projectKey, jira_key: jiraKey } },
          body: { testStatus },
        }),
      );
    },
    apiErrors: {
      STORY_SIGN_OFF_BLOCKED: t("errors.signOffBlocked"),
      INVALID_STATUS_TRANSITION: t("errors.invalidTransition"),
    },
    onSuccess: async (story, variables, onMutateResult, context) => {
      const queryKey: GetStoryQueryKey = [GET_STORY_KEY, projectKey, jiraKey];
      queryClient.setQueryData(queryKey, story);
      await queryClient.invalidateQueries({ queryKey: [GET_STORIES_KEY] });

      return onSuccess?.(story, variables, onMutateResult, context);
    },
    onError: async (error, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_STORY_KEY] });

      return onError?.(error, variables, onMutateResult, context);
    },
  });
};
