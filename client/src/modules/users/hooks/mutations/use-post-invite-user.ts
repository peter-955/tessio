"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { UserMutationOptions } from "../../typing/types/user-mutation-options.type";
import type { InviteUserRequest, WorkspaceUser } from "../../typing/types/workspace-user.type";
import { GET_WORKSPACE_USERS_KEY } from "../queries/use-get-workspace-users";
import { useUserApiErrors } from "../use-user-api-errors";

type Options = UserMutationOptions<WorkspaceUser, InviteUserRequest>;

export const usePostInviteUser = (
  options: Options = {},
): UseMutationResult<WorkspaceUser, ApiError, InviteUserRequest> => {
  const queryClient = useQueryClient();
  const apiErrors = useUserApiErrors();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<WorkspaceUser, InviteUserRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(apiClient.POST("/api/users", { body }));
    },
    apiErrors,
    isGlobalErrorToastDisabled: true,
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_WORKSPACE_USERS_KEY] });

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
