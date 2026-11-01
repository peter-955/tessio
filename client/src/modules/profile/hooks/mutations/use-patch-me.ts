"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_CURRENT_USER_KEY } from "@/modules/auth/hooks/queries/use-get-current-user";
import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { ProfileChanges } from "../../typing/types/profile-changes.type";
import type { ProfileMutationOptions } from "../../typing/types/profile-mutation-options.type";

type Options = ProfileMutationOptions<CurrentUser, ProfileChanges>;

export const usePatchMe = (
  options: Options = {},
): UseMutationResult<CurrentUser, ApiError, ProfileChanges> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<CurrentUser, ProfileChanges>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(apiClient.PATCH("/api/me", { body }));
    },
    onSuccess: (user, variables, onMutateResult, context) => {
      queryClient.setQueryData<CurrentUser>([GET_CURRENT_USER_KEY], user);

      return onSuccess?.(user, variables, onMutateResult, context);
    },
  });
};
