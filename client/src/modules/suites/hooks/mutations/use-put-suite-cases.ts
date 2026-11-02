"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { SuiteCaseIdsVariables } from "../../typing/types/suite-case-ids-variables.type";
import type { SuiteMutationOptions } from "../../typing/types/suite-mutation-options.type";
import type { SuiteDetail } from "../../typing/types/suite.type";
import { useSuiteApiErrors } from "../use-suite-api-errors";
import { useStoreSuite } from "../use-suite-cache";

type Options = SuiteMutationOptions<SuiteDetail, SuiteCaseIdsVariables>;

export const usePutSuiteCases = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<SuiteDetail, ApiError, SuiteCaseIdsVariables> => {
  const storeSuite = useStoreSuite(projectKey);
  const apiErrors = useSuiteApiErrors();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<SuiteDetail, SuiteCaseIdsVariables>({
    ...mutationOptions,
    mutationFn: ({ suiteId, testCaseIds }) => {
      return unwrapResponse(
        apiClient.PUT("/api/projects/{project_key}/suites/{suite_id}/cases", {
          params: { path: { project_key: projectKey, suite_id: suiteId } },
          body: { testCaseIds },
        }),
      );
    },
    apiErrors,
    onSuccess: async (suite, variables, onMutateResult, context) => {
      await storeSuite(suite);

      return onSuccess?.(suite, variables, onMutateResult, context);
    },
  });
};
