"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { skipToken, type UseQueryResult } from "@tanstack/react-query";
import type { JiraBoard } from "../../typing/types/jira.type";

export const GET_JIRA_BOARDS_KEY = "GET_JIRA_BOARDS_KEY";

export type GetJiraBoardsQueryKey = [typeof GET_JIRA_BOARDS_KEY, string | null];

type Result = Pick<
  UseQueryResult<JiraBoard[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetJiraBoards = (jiraProjectKey: string | null): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    JiraBoard[],
    GetJiraBoardsQueryKey
  >({
    queryKey: [GET_JIRA_BOARDS_KEY, jiraProjectKey],
    queryFn:
      jiraProjectKey === null
        ? skipToken
        : () => {
            return unwrapResponse(
              apiClient.GET("/api/workspace/jira/boards", {
                params: { query: { jiraProjectKey } },
              }),
            );
          },
    enabled: jiraProjectKey !== null,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
