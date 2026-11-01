"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { ManualCaseResultVariables } from "../../typing/types/manual-case-result-variables.type";
import type { ManualCaseResult } from "../../typing/types/manual-run.type";
import { GET_MANUAL_RUN_KEY, type GetManualRunQueryKey } from "../queries/use-get-manual-run";
import { useManualRunApiErrors } from "../use-manual-run-api-errors";

export const usePutManualCaseResult = (
  projectKey: string,
  runId: string,
): UseMutationResult<ManualCaseResult, ApiError, ManualCaseResultVariables> => {
  const queryClient = useQueryClient();
  const apiErrors = useManualRunApiErrors();

  return useAppMutation<ManualCaseResult, ManualCaseResultVariables>({
    mutationFn: ({ testCaseId, body }) => {
      return unwrapResponse(
        apiClient.PUT("/api/projects/{project_key}/runs/{run_id}/cases/{test_case_id}", {
          params: { path: { project_key: projectKey, run_id: runId, test_case_id: testCaseId } },
          body,
        }),
      );
    },
    apiErrors,
    isGlobalErrorToastDisabled: true,
    onSuccess: () => {
      const queryKey: GetManualRunQueryKey = [GET_MANUAL_RUN_KEY, projectKey, runId];

      return queryClient.invalidateQueries({ queryKey });
    },
  });
};
