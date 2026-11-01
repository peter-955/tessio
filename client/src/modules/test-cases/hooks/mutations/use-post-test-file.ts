"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { TestCaseMutationOptions } from "../../typing/types/test-case-mutation-options.type";
import type { AttachTestFileRequest, TestCaseDetail } from "../../typing/types/test-case.type";
import { useStoreTestCaseDetail } from "../use-store-test-case-detail";

type Options = TestCaseMutationOptions<TestCaseDetail, AttachTestFileRequest>;

export const usePostTestFile = (
  projectKey: string,
  caseCode: string,
  options: Options = {},
): UseMutationResult<TestCaseDetail, ApiError, AttachTestFileRequest> => {
  const storeDetail = useStoreTestCaseDetail(projectKey);
  const { t } = useTranslation("testCases");
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<TestCaseDetail, AttachTestFileRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/test-cases/{case_code}/files", {
          params: { path: { project_key: projectKey, case_code: caseCode } },
          body,
        }),
      );
    },
    apiErrors: {
      CONFLICT: t("errors.fileConflict"),
      UPLOAD_NOT_COMPLETED: t("errors.uploadNotCompleted"),
      FILE_TYPE_NOT_ALLOWED: t("errors.fileTypeNotAllowed"),
      FILE_TOO_LARGE: t("errors.fileTooLarge"),
    },
    onSuccess: async (detail, variables, onMutateResult, context) => {
      await storeDetail(detail, true);

      return onSuccess?.(detail, variables, onMutateResult, context);
    },
  });
};
