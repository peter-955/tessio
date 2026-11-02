"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { SuiteMutationOptions } from "../../typing/types/suite-mutation-options.type";
import type { SuiteUpdateVariables } from "../../typing/types/suite-update-variables.type";
import type { SuiteDetail } from "../../typing/types/suite.type";
import { useSuiteApiErrors } from "../use-suite-api-errors";
import { useStoreSuite } from "../use-suite-cache";

type Options = SuiteMutationOptions<SuiteDetail, SuiteUpdateVariables>;

export const usePatchSuite = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<SuiteDetail, ApiError, SuiteUpdateVariables> => {
  const storeSuite = useStoreSuite(projectKey);
  const apiErrors = useSuiteApiErrors();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<SuiteDetail, SuiteUpdateVariables>({
    ...mutationOptions,
    mutationFn: ({ suiteId, body }) => {
      return unwrapResponse(
        apiClient.PATCH("/api/projects/{project_key}/suites/{suite_id}", {
          params: { path: { project_key: projectKey, suite_id: suiteId } },
          body,
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
