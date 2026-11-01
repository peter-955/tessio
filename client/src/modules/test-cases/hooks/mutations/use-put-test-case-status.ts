"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { TestCaseMutationOptions } from "../../typing/types/test-case-mutation-options.type";
import type { TestCaseDetail, TestCaseStatus } from "../../typing/types/test-case.type";
import { GET_TEST_CASE_KEY } from "../queries/use-get-test-case";
import { useStoreTestCaseDetail } from "../use-store-test-case-detail";

type Options = TestCaseMutationOptions<TestCaseDetail, TestCaseStatus>;

export const usePutTestCaseStatus = (
  projectKey: string,
  caseCode: string,
  options: Options = {},
): UseMutationResult<TestCaseDetail, ApiError, TestCaseStatus> => {
  const queryClient = useQueryClient();
  const storeDetail = useStoreTestCaseDetail(projectKey);
  const { t } = useTranslation("testCases");
  const { onSuccess, onError, ...mutationOptions } = options;

  return useAppMutation<TestCaseDetail, TestCaseStatus>({
    ...mutationOptions,
    mutationFn: (status) => {
      return unwrapResponse(
        apiClient.PUT("/api/projects/{project_key}/test-cases/{case_code}/status", {
          params: { path: { project_key: projectKey, case_code: caseCode } },
          body: { status },
        }),
      );
    },
    apiErrors: {
      CASE_NOT_READY: t("errors.notReady"),
      UNKNOWN_REFERENCE: t("errors.unknownReferences"),
      INVALID_STATUS_TRANSITION: t("errors.invalidTransition"),
    },
    onSuccess: async (detail, variables, onMutateResult, context) => {
      await storeDetail(detail);

      return onSuccess?.(detail, variables, onMutateResult, context);
    },
    onError: async (error, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_TEST_CASE_KEY, projectKey, caseCode] });

      return onError?.(error, variables, onMutateResult, context);
    },
  });
};
