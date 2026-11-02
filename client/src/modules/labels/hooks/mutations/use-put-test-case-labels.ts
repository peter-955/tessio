"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import {
  GET_TEST_CASE_KEY,
  type GetTestCaseQueryKey,
} from "@/modules/test-cases/hooks/queries/use-get-test-case";
import { GET_TEST_CASES_KEY } from "@/modules/test-cases/hooks/queries/use-get-test-cases";
import type { TestCaseDetail } from "@/modules/test-cases/typing/types/test-case.type";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { LabelMutationOptions } from "../../typing/types/label-mutation-options.type";
import type { CaseLabel } from "../../typing/types/label.type";
import { GET_LABELS_KEY } from "../queries/use-get-labels";

type Options = LabelMutationOptions<CaseLabel[], string[]>;

export const usePutTestCaseLabels = (
  projectKey: string,
  caseCode: string,
  options: Options = {},
): UseMutationResult<CaseLabel[], ApiError, string[]> => {
  const queryClient = useQueryClient();
  const { t } = useTranslation("labels");
  const { onSuccess, onError, ...mutationOptions } = options;

  return useAppMutation<CaseLabel[], string[]>({
    ...mutationOptions,
    mutationFn: (labelIds) => {
      return unwrapResponse(
        apiClient.PUT("/api/projects/{project_key}/test-cases/{case_code}/labels", {
          params: { path: { project_key: projectKey, case_code: caseCode } },
          body: { labelIds },
        }),
      );
    },
    apiErrors: { INVALID_REQUEST: t("errors.notProjectLabel") },
    onSuccess: async (labels, variables, onMutateResult, context) => {
      const queryKey: GetTestCaseQueryKey = [GET_TEST_CASE_KEY, projectKey, caseCode];
      queryClient.setQueryData<TestCaseDetail>(queryKey, (detail) => {
        return detail === undefined ? detail : { ...detail, labels };
      });
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: [GET_TEST_CASES_KEY, projectKey] }),
        queryClient.invalidateQueries({ queryKey: [GET_LABELS_KEY, projectKey] }),
      ]);

      return onSuccess?.(labels, variables, onMutateResult, context);
    },
    onError: async (error, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_LABELS_KEY, projectKey] });

      return onError?.(error, variables, onMutateResult, context);
    },
  });
};
