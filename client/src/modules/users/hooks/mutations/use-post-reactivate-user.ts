"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { UserMutationOptions } from "../../typing/types/user-mutation-options.type";
import type { WorkspaceUser } from "../../typing/types/workspace-user.type";
import { useInvalidateWorkspaceUsers } from "../use-invalidate-workspace-users";
import { useUserApiErrors } from "../use-user-api-errors";

type Options = UserMutationOptions<WorkspaceUser, string>;

export const usePostReactivateUser = (
  options: Options = {},
): UseMutationResult<WorkspaceUser, ApiError, string> => {
  const invalidateWorkspaceUsers = useInvalidateWorkspaceUsers();
  const apiErrors = useUserApiErrors();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<WorkspaceUser, string>({
    ...mutationOptions,
    mutationFn: (userId) => {
      return unwrapResponse(
        apiClient.POST("/api/users/{user_id}/reactivate", {
          params: { path: { user_id: userId } },
        }),
      );
    },
    apiErrors,
    onSuccess: async (data, userId, onMutateResult, context) => {
      await invalidateWorkspaceUsers(userId, { hasProjectMembers: true });

      return onSuccess?.(data, userId, onMutateResult, context);
    },
  });
};
