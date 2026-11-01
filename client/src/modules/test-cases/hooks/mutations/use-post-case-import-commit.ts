"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { TestCaseMutationOptions } from "../../typing/types/test-case-mutation-options.type";
import type { CaseImportCommitRequest, CaseImportResult } from "../../typing/types/test-case.type";
import { GET_TEST_CASES_KEY } from "../queries/use-get-test-cases";

type Options = TestCaseMutationOptions<CaseImportResult, CaseImportCommitRequest>;

export const usePostCaseImportCommit = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<CaseImportResult, ApiError, CaseImportCommitRequest> => {
  const queryClient = useQueryClient();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<CaseImportResult, CaseImportCommitRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/test-case-imports/commit", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
    onSuccess: async (result, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_TEST_CASES_KEY] });

      return onSuccess?.(result, variables, onMutateResult, context);
    },
  });
};
