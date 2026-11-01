"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { TestCaseMutationOptions } from "../../typing/types/test-case-mutation-options.type";
import type {
  CaseImportPreview,
  CaseImportPreviewRequest,
} from "../../typing/types/test-case.type";

type Options = TestCaseMutationOptions<CaseImportPreview, CaseImportPreviewRequest>;

export const usePostCaseImportPreview = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<CaseImportPreview, ApiError, CaseImportPreviewRequest> => {
  return useAppMutation<CaseImportPreview, CaseImportPreviewRequest>({
    ...options,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/test-case-imports/preview", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
  });
};
