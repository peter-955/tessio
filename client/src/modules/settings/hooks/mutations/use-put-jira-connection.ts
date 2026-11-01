"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_JIRA_BOARDS_KEY } from "@/modules/projects/hooks/queries/use-get-jira-boards";
import { GET_JIRA_PROJECTS_KEY } from "@/modules/projects/hooks/queries/use-get-jira-projects";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { JiraConnectionChange } from "../../typing/types/jira-connection-change.type";
import type { JiraConnection } from "../../typing/types/jira-connection.type";
import { GET_JIRA_CONNECTION_KEY } from "../queries/use-get-jira-connection";

type Result = Pick<
  UseMutationResult<JiraConnection, ApiError, JiraConnectionChange>,
  "mutate" | "isPending" | "error" | "reset"
>;

export const usePutJiraConnection = (): Result => {
  const queryClient = useQueryClient();
  const { mutate, isPending, error, reset } = useAppMutation<JiraConnection, JiraConnectionChange>({
    mutationFn: (body) => {
      return unwrapResponse(apiClient.PUT("/api/workspace/jira", { body }));
    },
    isGlobalErrorToastDisabled: true,
    onSuccess: (connection) => {
      queryClient.setQueryData([GET_JIRA_CONNECTION_KEY], connection);
      void queryClient.invalidateQueries({ queryKey: [GET_JIRA_PROJECTS_KEY] });
      void queryClient.invalidateQueries({ queryKey: [GET_JIRA_BOARDS_KEY] });
    },
  });

  return { mutate, isPending, error, reset };
};
