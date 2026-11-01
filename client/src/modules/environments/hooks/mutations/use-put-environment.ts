"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_ENVIRONMENTS_KEY } from "@/shared/hooks/queries/use-get-environments";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { EnvironmentMutationOptions } from "../../typing/types/environment-mutation-options.type";
import type { EnvironmentUpdate } from "../../typing/types/environment-update.type";
import type { Environment } from "../../typing/types/environment.type";

type Options = EnvironmentMutationOptions<Environment, EnvironmentUpdate>;

export const usePutEnvironment = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<Environment, ApiError, EnvironmentUpdate> => {
  const queryClient = useQueryClient();
  const { t } = useTranslation("environments");
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<Environment, EnvironmentUpdate>({
    ...mutationOptions,
    mutationFn: ({ environmentId, body }) => {
      return unwrapResponse(
        apiClient.PUT("/api/projects/{project_key}/environments/{environment_id}", {
          params: { path: { project_key: projectKey, environment_id: environmentId } },
          body,
        }),
      );
    },
    apiErrors: { ENVIRONMENT_NAME_ALREADY_USED: t("errors.nameAlreadyUsed") },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_ENVIRONMENTS_KEY] });

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
