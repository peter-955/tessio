"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { SuiteMutationOptions } from "../../typing/types/suite-mutation-options.type";
import type { CreateSuiteRequest, SuiteDetail } from "../../typing/types/suite.type";
import { useSuiteApiErrors } from "../use-suite-api-errors";
import { useStoreSuite } from "../use-suite-cache";

type Options = SuiteMutationOptions<SuiteDetail, CreateSuiteRequest>;

export const usePostSuite = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<SuiteDetail, ApiError, CreateSuiteRequest> => {
  const storeSuite = useStoreSuite(projectKey);
  const apiErrors = useSuiteApiErrors();
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<SuiteDetail, CreateSuiteRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/suites", {
          params: { path: { project_key: projectKey } },
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
