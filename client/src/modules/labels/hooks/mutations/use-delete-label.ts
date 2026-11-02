"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_TEST_CASE_KEY } from "@/modules/test-cases/hooks/queries/use-get-test-case";
import { GET_TEST_CASES_KEY } from "@/modules/test-cases/hooks/queries/use-get-test-cases";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { LabelMutationOptions } from "../../typing/types/label-mutation-options.type";
import { GET_LABELS_KEY } from "../queries/use-get-labels";

type Options = LabelMutationOptions<void, string>;

export const useDeleteLabel = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<void, ApiError, string> => {
  const queryClient = useQueryClient();
  const { t } = useTranslation("labels");
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<void, string>({
    ...mutationOptions,
    mutationFn: (labelId) => {
      return unwrapResponse(
        apiClient.DELETE("/api/projects/{project_key}/labels/{label_id}", {
          params: { path: { project_key: projectKey, label_id: labelId } },
        }),
      );
    },
    apiErrors: { NOT_FOUND: t("errors.notFound") },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: [GET_LABELS_KEY, projectKey] }),
        queryClient.invalidateQueries({ queryKey: [GET_TEST_CASES_KEY, projectKey] }),
        queryClient.invalidateQueries({ queryKey: [GET_TEST_CASE_KEY, projectKey] }),
      ]);

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
