"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { UserMutationOptions } from "../../typing/types/user-mutation-options.type";
import type { WorkspaceRoleChange } from "../../typing/types/workspace-role-change.type";
import type { WorkspaceUser } from "../../typing/types/workspace-user.type";
import { useInvalidateWorkspaceUsers } from "../use-invalidate-workspace-users";
import { useUserApiErrors } from "../use-user-api-errors";

type Options = UserMutationOptions<WorkspaceUser, WorkspaceRoleChange>;

export const usePutWorkspaceRole = (
  options: Options = {},
): UseMutationResult<WorkspaceUser, ApiError, WorkspaceRoleChange> => {
  const invalidateWorkspaceUsers = useInvalidateWorkspaceUsers();
  const apiErrors = useUserApiErrors();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<WorkspaceUser, WorkspaceRoleChange>({
    ...mutationOptions,
    mutationFn: ({ userId, workspaceRole }) => {
      return unwrapResponse(
        apiClient.PUT("/api/users/{user_id}/workspace-role", {
          params: { path: { user_id: userId } },
          body: { workspaceRole },
        }),
      );
    },
    apiErrors,
    onSuccess: async (data, variables, onMutateResult, context) => {
      await invalidateWorkspaceUsers(variables.userId);

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
