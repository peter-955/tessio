"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { TestCaseMutationOptions } from "../../typing/types/test-case-mutation-options.type";
import type { CreateTestCaseRequest, TestCaseDetail } from "../../typing/types/test-case.type";
import { useStoreTestCaseDetail } from "../use-store-test-case-detail";

type Options = TestCaseMutationOptions<TestCaseDetail, CreateTestCaseRequest>;

export const usePostTestCase = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<TestCaseDetail, ApiError, CreateTestCaseRequest> => {
  const storeDetail = useStoreTestCaseDetail(projectKey);
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<TestCaseDetail, CreateTestCaseRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/test-cases", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
    onSuccess: async (detail, variables, onMutateResult, context) => {
      await storeDetail(detail);

      return onSuccess?.(detail, variables, onMutateResult, context);
    },
  });
};
