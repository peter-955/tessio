"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { ManualFinishRequest, ManualRunCreated } from "../../typing/types/manual-run.type";
import { GET_MANUAL_RUN_KEY, type GetManualRunQueryKey } from "../queries/use-get-manual-run";
import { useManualRunApiErrors } from "../use-manual-run-api-errors";

export const usePostManualRunFinish = (
  projectKey: string,
  runId: string,
): UseMutationResult<ManualRunCreated, ApiError, ManualFinishRequest> => {
  const queryClient = useQueryClient();
  const apiErrors = useManualRunApiErrors();

  return useAppMutation<ManualRunCreated, ManualFinishRequest>({
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/runs/{run_id}/finish", {
          params: { path: { project_key: projectKey, run_id: runId } },
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
