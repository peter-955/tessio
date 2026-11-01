"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_ENVIRONMENTS_KEY } from "@/shared/hooks/queries/use-get-environments";
import { GET_PROJECT_KEY } from "@/shared/hooks/queries/use-get-project";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { EnvironmentMutationOptions } from "../../typing/types/environment-mutation-options.type";
import type { Environment } from "../../typing/types/environment.type";

type Options = EnvironmentMutationOptions<Environment, string>;

export const usePostUnarchiveEnvironment = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<Environment, ApiError, string> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<Environment, string>({
    ...mutationOptions,
    mutationFn: (environmentId) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/environments/{environment_id}/unarchive", {
          params: { path: { project_key: projectKey, environment_id: environmentId } },
        }),
      );
    },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: [GET_ENVIRONMENTS_KEY] }),
        queryClient.invalidateQueries({ queryKey: [GET_PROJECT_KEY] }),
      ]);

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
