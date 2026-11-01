"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { ImportCommitRequest, ImportResult } from "../../typing/types/import.type";
import type { TestDataMutationOptions } from "../../typing/types/test-data-mutation-options.type";
import { GET_TEST_DATA_KEY } from "../queries/use-get-test-data";

type Options = TestDataMutationOptions<ImportResult, ImportCommitRequest>;

export const usePostImportCommit = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<ImportResult, ApiError, ImportCommitRequest> => {
  const queryClient = useQueryClient();
  const { t } = useTranslation("testData");
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<ImportResult, ImportCommitRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/test-data/import/commit", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
    apiErrors: {
      IMPORT_INVALID_FILE: t("import.errors.invalidFile"),
      UPLOAD_NOT_COMPLETED: t("import.errors.uploadNotCompleted"),
    },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_TEST_DATA_KEY] });

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
