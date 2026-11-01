"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { Gap } from "../../typing/types/gap.type";

export const GET_STORY_GAPS_KEY = "GET_STORY_GAPS_KEY";

export type GetStoryGapsQueryKey = [typeof GET_STORY_GAPS_KEY, string, string];

type Result = Pick<
  UseQueryResult<Gap[], ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetStoryGaps = (projectKey: string, storyKey: string): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    Gap[],
    GetStoryGapsQueryKey
  >({
    queryKey: [GET_STORY_GAPS_KEY, projectKey, storyKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/gaps", {
          params: { path: { project_key: projectKey }, query: { storyKey } },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError, isFetching, refetch };
};
