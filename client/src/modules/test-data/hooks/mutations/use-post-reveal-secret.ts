"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { RevealedSecret } from "../../typing/types/data-item.type";
import type { TestDataMutationOptions } from "../../typing/types/test-data-mutation-options.type";

type Options = TestDataMutationOptions<RevealedSecret, string>;

export const usePostRevealSecret = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<RevealedSecret, ApiError, string> => {
  return useAppMutation<RevealedSecret, string>({
    ...options,
    gcTime: 0,
    mutationFn: (itemId) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/test-data/{item_id}/reveal", {
          params: { path: { project_key: projectKey, item_id: itemId } },
        }),
      );
    },
  });
};
