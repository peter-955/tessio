"use client";

import type { DSSelectOption } from "@/components/design-system";
import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { STORY_OPTIONS_STALE_TIME_IN_MILLISECONDS } from "../../typing/constants/run.constant";

export const GET_RUN_STORY_OPTIONS_KEY = "GET_RUN_STORY_OPTIONS_KEY";

export type GetRunStoryOptionsQueryKey = [typeof GET_RUN_STORY_OPTIONS_KEY, string];

type Result = Pick<UseQueryResult<DSSelectOption<string>[], ApiError>, "data" | "isPending">;

export const useGetRunStoryOptions = (projectKey: string): Result => {
  const { data, isPending } = useAppQuery<DSSelectOption<string>[], GetRunStoryOptionsQueryKey>({
    queryKey: [GET_RUN_STORY_OPTIONS_KEY, projectKey],
    queryFn: async ({ signal }) => {
      const stories = await unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/stories", {
          params: { path: { project_key: projectKey } },
          signal,
        }),
      );

      return stories.map((story): DSSelectOption<string> => {
        return { value: story.jiraKey, label: `${story.jiraKey} · ${story.title}` };
      });
    },
    staleTime: STORY_OPTIONS_STALE_TIME_IN_MILLISECONDS,
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending };
};
