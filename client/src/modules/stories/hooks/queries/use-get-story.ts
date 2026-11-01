"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { StoryDetail } from "../../typing/types/story.type";

export const GET_STORY_KEY = "GET_STORY_KEY";

export type GetStoryQueryKey = [typeof GET_STORY_KEY, string, string];

type Result = Pick<
  UseQueryResult<StoryDetail, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetStory = (projectKey: string, jiraKey: string): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    StoryDetail,
    GetStoryQueryKey
  >({
    queryKey: [GET_STORY_KEY, projectKey, jiraKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/stories/{jira_key}", {
          params: { path: { project_key: projectKey, jira_key: jiraKey } },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
