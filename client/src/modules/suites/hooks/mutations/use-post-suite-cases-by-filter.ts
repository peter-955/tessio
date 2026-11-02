"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { SuiteFilterVariables } from "../../typing/types/suite-filter-variables.type";
import type { SuiteMutationOptions } from "../../typing/types/suite-mutation-options.type";
import type { SuiteCasesAdded } from "../../typing/types/suite.type";
import { useSuiteApiErrors } from "../use-suite-api-errors";
import { useStoreSuite } from "../use-suite-cache";

type Options = SuiteMutationOptions<SuiteCasesAdded, SuiteFilterVariables>;

export const usePostSuiteCasesByFilter = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<SuiteCasesAdded, ApiError, SuiteFilterVariables> => {
  const storeSuite = useStoreSuite(projectKey);
  const apiErrors = useSuiteApiErrors();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<SuiteCasesAdded, SuiteFilterVariables>({
    ...mutationOptions,
    mutationFn: ({ suiteId, body }) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/suites/{suite_id}/cases/by-filter", {
          params: { path: { project_key: projectKey, suite_id: suiteId } },
          body,
        }),
      );
    },
    apiErrors,
    onSuccess: async (added, variables, onMutateResult, context) => {
      await storeSuite(added.suite);

      return onSuccess?.(added, variables, onMutateResult, context);
    },
  });
};
