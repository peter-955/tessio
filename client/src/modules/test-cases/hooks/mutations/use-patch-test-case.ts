"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { TestCaseMutationOptions } from "../../typing/types/test-case-mutation-options.type";
import type { TestCaseDetail, UpdateTestCaseRequest } from "../../typing/types/test-case.type";
import { useStoreTestCaseDetail } from "../use-store-test-case-detail";

type Options = TestCaseMutationOptions<TestCaseDetail, UpdateTestCaseRequest>;

export const usePatchTestCase = (
  projectKey: string,
  caseCode: string,
  options: Options = {},
): UseMutationResult<TestCaseDetail, ApiError, UpdateTestCaseRequest> => {
  const storeDetail = useStoreTestCaseDetail(projectKey);
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<TestCaseDetail, UpdateTestCaseRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.PATCH("/api/projects/{project_key}/test-cases/{case_code}", {
          params: { path: { project_key: projectKey, case_code: caseCode } },
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
