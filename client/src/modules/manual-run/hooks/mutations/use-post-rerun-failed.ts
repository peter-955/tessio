"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { ManualRerunRequest, ManualRunCreated } from "../../typing/types/manual-run.type";
import { useManualRunApiErrors } from "../use-manual-run-api-errors";

export const usePostRerunFailed = (
  projectKey: string,
  runId: string,
): UseMutationResult<ManualRunCreated, ApiError, ManualRerunRequest> => {
  const apiErrors = useManualRunApiErrors();

  return useAppMutation<ManualRunCreated, ManualRerunRequest>({
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/runs/{run_id}/rerun-failed", {
          params: { path: { project_key: projectKey, run_id: runId } },
          body,
        }),
      );
    },
    apiErrors,
    isGlobalErrorToastDisabled: true,
  });
};
