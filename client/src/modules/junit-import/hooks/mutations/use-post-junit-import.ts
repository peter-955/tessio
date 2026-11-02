"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_RECENT_RUNS_KEY } from "@/modules/dashboard/hooks/queries/use-get-recent-runs";
import { GET_RUNS_KEY } from "@/modules/runs/hooks/queries/use-get-runs";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { JunitImportMutationOptions } from "../../typing/types/junit-import-mutation-options.type";
import type {
  JunitImport,
  JunitImportFormFields,
  JunitImportRequest,
} from "../../typing/types/junit-import.type";
import { buildJunitImportFormData } from "../../utils/junit-import-form-data.util";

type Options = JunitImportMutationOptions<JunitImport, JunitImportRequest>;

export const usePostJunitImport = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<JunitImport, ApiError, JunitImportRequest> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<JunitImport, JunitImportRequest>({
    ...mutationOptions,
    mutationFn: (request) => {
      const fields: JunitImportFormFields = {
        file: request.file.name,
        environment: request.environment,
        suite: request.suite,
      };

      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/runs/import", {
          params: { path: { project_key: projectKey } },
          body: fields,
          bodySerializer: () => {
            return buildJunitImportFormData(request);
          },
        }),
      );
    },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: [GET_RUNS_KEY, projectKey] }),
        queryClient.invalidateQueries({ queryKey: [GET_RECENT_RUNS_KEY, projectKey] }),
      ]);

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
