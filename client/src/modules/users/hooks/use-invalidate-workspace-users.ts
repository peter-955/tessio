"use client";

import { GET_PROJECT_MEMBERS_KEY } from "@/shared/hooks/queries/use-get-project-members";
import { useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import { GET_WORKSPACE_USER_KEY } from "./queries/use-get-workspace-user";
import { GET_WORKSPACE_USERS_KEY } from "./queries/use-get-workspace-users";

interface InvalidateOptions {
  hasProjectMembers?: boolean;
}

export const useInvalidateWorkspaceUsers = (): ((
  userId: string,
  options?: InvalidateOptions,
) => Promise<void>) => {
  const queryClient = useQueryClient();

  return useCallback(
    async (
      userId: string,
      { hasProjectMembers = false }: InvalidateOptions = {},
    ): Promise<void> => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: [GET_WORKSPACE_USERS_KEY] }),
        queryClient.invalidateQueries({ queryKey: [GET_WORKSPACE_USER_KEY, userId] }),
        ...(hasProjectMembers
          ? [queryClient.invalidateQueries({ queryKey: [GET_PROJECT_MEMBERS_KEY] })]
          : []),
      ]);
    },
    [queryClient],
  );
};
