"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { StoryMutationOptions } from "../../typing/types/story-mutation-options.type";
import type { ProjectSyncState } from "../../typing/types/story.type";
import { GET_SYNC_STATUS_KEY, type GetSyncStatusQueryKey } from "../queries/use-get-sync-status";

type Options = StoryMutationOptions<ProjectSyncState, void>;

export const usePostSync = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<ProjectSyncState, ApiError, void> => {
  const queryClient = useQueryClient();
  const { t } = useTranslation("stories");
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<ProjectSyncState, void>({
    ...mutationOptions,
    mutationFn: () => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/sync", {
          params: { path: { project_key: projectKey } },
        }),
      );
    },
    apiErrors: { JIRA_NOT_CONFIGURED: t("errors.jiraNotConfigured") },
    onSuccess: (state, variables, onMutateResult, context) => {
      const queryKey: GetSyncStatusQueryKey = [GET_SYNC_STATUS_KEY, projectKey];
      queryClient.setQueryData(queryKey, state);

      return onSuccess?.(state, variables, onMutateResult, context);
    },
  });
};
