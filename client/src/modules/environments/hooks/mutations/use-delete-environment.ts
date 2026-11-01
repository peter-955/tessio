"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_TEST_DATA_KEY } from "@/modules/test-data/hooks/queries/use-get-test-data";
import { GET_ENVIRONMENTS_KEY } from "@/shared/hooks/queries/use-get-environments";
import { GET_PROJECT_KEY } from "@/shared/hooks/queries/use-get-project";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { EnvironmentMutationOptions } from "../../typing/types/environment-mutation-options.type";

type Options = EnvironmentMutationOptions<void, string>;

export const useDeleteEnvironment = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<void, ApiError, string> => {
  const queryClient = useQueryClient();
  const { t } = useTranslation("environments");
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<void, string>({
    ...mutationOptions,
    mutationFn: (environmentId) => {
      return unwrapResponse(
        apiClient.DELETE("/api/projects/{project_key}/environments/{environment_id}", {
          params: { path: { project_key: projectKey, environment_id: environmentId } },
        }),
      );
    },
    apiErrors: { ENVIRONMENT_IN_USE: t("errors.inUse") },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: [GET_ENVIRONMENTS_KEY] }),
        queryClient.invalidateQueries({ queryKey: [GET_PROJECT_KEY] }),
        queryClient.invalidateQueries({ queryKey: [GET_TEST_DATA_KEY] }),
      ]);

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
