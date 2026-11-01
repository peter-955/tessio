"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { skipToken, type UseQueryResult } from "@tanstack/react-query";
import type { JiraProject } from "../../typing/types/jira.type";

export const GET_JIRA_PROJECTS_KEY = "GET_JIRA_PROJECTS_KEY";

export type GetJiraProjectsQueryKey = [typeof GET_JIRA_PROJECTS_KEY];

interface Options {
  isEnabled: boolean;
}

type Result = Pick<
  UseQueryResult<JiraProject[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetJiraProjects = ({ isEnabled }: Options): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    JiraProject[],
    GetJiraProjectsQueryKey
  >({
    queryKey: [GET_JIRA_PROJECTS_KEY],
    queryFn: isEnabled
      ? () => {
          return unwrapResponse(apiClient.GET("/api/workspace/jira/projects"));
        }
      : skipToken,
    enabled: isEnabled,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
