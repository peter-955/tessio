"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { StoryMutationOptions } from "../../typing/types/story-mutation-options.type";
import { GET_STORIES_KEY } from "../queries/use-get-stories";

export const useDeleteStory = (
  projectKey: string,
  jiraKey: string,
  options: StoryMutationOptions<void, void> = {},
): UseMutationResult<void, ApiError, void> => {
  const queryClient = useQueryClient();
  const { t } = useTranslation("stories");
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<void, void>({
    ...mutationOptions,
    mutationFn: () => {
      return unwrapResponse(
        apiClient.DELETE("/api/projects/{project_key}/stories/{jira_key}", {
          params: { path: { project_key: projectKey, jira_key: jiraKey } },
        }),
      );
    },
    apiErrors: { CONFLICT: t("editor.inUse") },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_STORIES_KEY] });

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
