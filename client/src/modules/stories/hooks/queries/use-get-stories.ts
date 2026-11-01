"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { keepPreviousData, type UseQueryResult } from "@tanstack/react-query";
import type { StoryFilters } from "../../typing/types/story-filters.type";
import type { StorySummary, TestStatus } from "../../typing/types/story.type";
import { buildStoryListQuery } from "../../utils/story-filters.util";

export const GET_STORIES_KEY = "GET_STORIES_KEY";

export type GetStoriesQueryKey = [
  typeof GET_STORIES_KEY,
  string,
  string | null,
  TestStatus | null,
  string,
];

type Result = Pick<
  UseQueryResult<StorySummary[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetStories = (projectKey: string, filters: StoryFilters): Result => {
  const trimmedQuery = filters.query.trim();
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    StorySummary[],
    GetStoriesQueryKey
  >({
    queryKey: [GET_STORIES_KEY, projectKey, filters.sprintId, filters.testStatus, trimmedQuery],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/stories", {
          params: { path: { project_key: projectKey }, query: buildStoryListQuery(filters) },
          signal,
        }),
      );
    },
    placeholderData: keepPreviousData,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
