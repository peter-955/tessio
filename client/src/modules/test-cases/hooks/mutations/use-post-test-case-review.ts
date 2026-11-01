"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { TestCaseMutationOptions } from "../../typing/types/test-case-mutation-options.type";
import type { TestCaseDetail } from "../../typing/types/test-case.type";
import { useStoreTestCaseDetail } from "../use-store-test-case-detail";

type Options = TestCaseMutationOptions<TestCaseDetail, void>;

export const usePostTestCaseReview = (
  projectKey: string,
  caseCode: string,
  options: Options = {},
): UseMutationResult<TestCaseDetail, ApiError, void> => {
  const storeDetail = useStoreTestCaseDetail(projectKey);
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<TestCaseDetail, void>({
    ...mutationOptions,
    mutationFn: () => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/test-cases/{case_code}/review", {
          params: { path: { project_key: projectKey, case_code: caseCode } },
        }),
      );
    },
    onSuccess: async (detail, variables, onMutateResult, context) => {
      await storeDetail(detail);

      return onSuccess?.(detail, variables, onMutateResult, context);
    },
  });
};
