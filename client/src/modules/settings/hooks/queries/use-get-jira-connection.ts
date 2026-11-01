"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { skipToken, type UseQueryResult } from "@tanstack/react-query";
import type { JiraConnection } from "../../typing/types/jira-connection.type";

export const GET_JIRA_CONNECTION_KEY = "GET_JIRA_CONNECTION_KEY";

export type GetJiraConnectionQueryKey = [typeof GET_JIRA_CONNECTION_KEY];

interface Options {
  isEnabled: boolean;
}

type Result = Pick<
  UseQueryResult<JiraConnection, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetJiraConnection = ({ isEnabled }: Options): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    JiraConnection,
    GetJiraConnectionQueryKey
  >({
    queryKey: [GET_JIRA_CONNECTION_KEY],
    queryFn: isEnabled
      ? () => {
          return unwrapResponse(apiClient.GET("/api/workspace/jira"));
        }
      : skipToken,
    enabled: isEnabled,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
