"use client";

import { ApiError } from "@/lib/api/api-error";
import { GET_CURRENT_USER_KEY } from "@/modules/auth/hooks/queries/use-get-current-user";
import { UNAUTHORIZED_STATUS } from "@/modules/auth/typing/constants/http-status.constant";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

const isUnauthorizedError = (error: unknown): boolean => {
  return error instanceof ApiError && error.status === UNAUTHORIZED_STATUS;
};

export const useRefetchCurrentUserOnUnauthorized = (): void => {
  const queryClient = useQueryClient();

  useEffect(() => {
    const invalidateCurrentUser = (): void => {
      void queryClient.invalidateQueries({ queryKey: [GET_CURRENT_USER_KEY] });
    };

    const unsubscribeFromQueries = queryClient.getQueryCache().subscribe((event) => {
      if (
        event.type === "updated" &&
        event.action.type === "error" &&
        event.query.queryKey[0] !== GET_CURRENT_USER_KEY &&
        isUnauthorizedError(event.action.error)
      ) {
        invalidateCurrentUser();
      }
    });
    const unsubscribeFromMutations = queryClient.getMutationCache().subscribe((event) => {
      if (
        event.type === "updated" &&
        event.action.type === "error" &&
        isUnauthorizedError(event.action.error)
      ) {
        invalidateCurrentUser();
      }
    });

    return (): void => {
      unsubscribeFromQueries();
      unsubscribeFromMutations();
    };
  }, [queryClient]);
};
