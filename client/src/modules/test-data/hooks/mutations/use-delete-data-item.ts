"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { TestDataMutationOptions } from "../../typing/types/test-data-mutation-options.type";
import { GET_TEST_DATA_KEY } from "../queries/use-get-test-data";

type Options = TestDataMutationOptions<void, string>;

export const useDeleteDataItem = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<void, ApiError, string> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<void, string>({
    ...mutationOptions,
    mutationFn: (itemId) => {
      return unwrapResponse(
        apiClient.DELETE("/api/projects/{project_key}/test-data/{item_id}", {
          params: { path: { project_key: projectKey, item_id: itemId } },
        }),
      );
    },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_TEST_DATA_KEY] });

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
