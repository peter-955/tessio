"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_ENVIRONMENTS_KEY } from "@/shared/hooks/queries/use-get-environments";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { EnvironmentMutationOptions } from "../../typing/types/environment-mutation-options.type";
import type { Environment, EnvironmentRequest } from "../../typing/types/environment.type";

type Options = EnvironmentMutationOptions<Environment, EnvironmentRequest>;

export const usePostEnvironment = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<Environment, ApiError, EnvironmentRequest> => {
  const queryClient = useQueryClient();
  const { t } = useTranslation("environments");
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<Environment, EnvironmentRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/environments", {
          params: { path: { project_key: projectKey } },
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
