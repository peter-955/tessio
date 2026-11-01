"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { RunStory } from "../../typing/types/manual-run.type";

export const GET_RUN_STORIES_KEY = "GET_RUN_STORIES_KEY";

export type GetRunStoriesQueryKey = [typeof GET_RUN_STORIES_KEY, string];

type Result = Pick<UseQueryResult<RunStory[], ApiError>, "data" | "isPending" | "isError">;

export const useGetRunStories = (projectKey: string): Result => {
  const { data, isPending, isError } = useAppQuery<RunStory[], GetRunStoriesQueryKey>({
    queryKey: [GET_RUN_STORIES_KEY, projectKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/stories", {
          params: { path: { project_key: projectKey } },
          signal,
        }),
      );
    },
  });

  return { data, isPending, isError };
};
