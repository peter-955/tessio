"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import type { StoryProgress } from "@/modules/traceability/typing/types/traceability.type";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { keepPreviousData, type UseQueryResult } from "@tanstack/react-query";

export const GET_STORY_PROGRESS_KEY = "GET_STORY_PROGRESS_KEY";

export type GetStoryProgressQueryKey = [typeof GET_STORY_PROGRESS_KEY, string, string | null];

type Result = Pick<UseQueryResult<StoryProgress[], ApiError>, "data" | "isPending" | "isError">;

export const useGetStoryProgress = (projectKey: string, sprintId: string | null): Result => {
  const { data, isPending, isError } = useAppQuery<StoryProgress[], GetStoryProgressQueryKey>({
    queryKey: [GET_STORY_PROGRESS_KEY, projectKey, sprintId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/story-progress", {
          params: {
            path: { project_key: projectKey },
            query: sprintId === null ? {} : { sprintId },
          },
          signal,
        }),
      );
    },
    placeholderData: keepPreviousData,
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError };
};
