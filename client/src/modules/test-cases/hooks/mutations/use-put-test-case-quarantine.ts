"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { QuarantineTestCaseRequest } from "../../typing/types/quarantine.type";
import type { TestCaseMutationOptions } from "../../typing/types/test-case-mutation-options.type";
import type { TestCaseDetail } from "../../typing/types/test-case.type";
import { useStoreQuarantineChange } from "../use-store-quarantine-change";

type Options = TestCaseMutationOptions<TestCaseDetail, QuarantineTestCaseRequest>;

export const usePutTestCaseQuarantine = (
  projectKey: string,
  caseCode: string,
  options: Options = {},
): UseMutationResult<TestCaseDetail, ApiError, QuarantineTestCaseRequest> => {
  const storeChange = useStoreQuarantineChange(projectKey);
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<TestCaseDetail, QuarantineTestCaseRequest>({
    ...mutationOptions,
    mutationFn: (request) => {
      return unwrapResponse(
        apiClient.PUT("/api/projects/{project_key}/test-cases/{case_code}/quarantine", {
          params: { path: { project_key: projectKey, case_code: caseCode } },
          body: request,
        }),
      );
    },
    onSuccess: async (detail, variables, onMutateResult, context) => {
      await storeChange(detail);

      return onSuccess?.(detail, variables, onMutateResult, context);
    },
  });
};
