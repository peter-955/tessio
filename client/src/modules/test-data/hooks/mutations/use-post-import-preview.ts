"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { ImportPreview, ImportPreviewRequest } from "../../typing/types/import.type";
import type { TestDataMutationOptions } from "../../typing/types/test-data-mutation-options.type";

type Options = TestDataMutationOptions<ImportPreview, ImportPreviewRequest>;

export const usePostImportPreview = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<ImportPreview, ApiError, ImportPreviewRequest> => {
  const { t } = useTranslation("testData");

  return useAppMutation<ImportPreview, ImportPreviewRequest>({
    ...options,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/test-data/import/preview", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
    apiErrors: {
      IMPORT_INVALID_FILE: t("import.errors.invalidFile"),
      FILE_TOO_LARGE: t("import.errors.size"),
      UPLOAD_NOT_COMPLETED: t("import.errors.uploadNotCompleted"),
    },
  });
};
