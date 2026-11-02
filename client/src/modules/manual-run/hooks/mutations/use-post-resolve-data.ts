"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { ResolveDataRequest, ResolvedData } from "../../typing/types/manual-run.type";
import { useManualRunApiErrors } from "../use-manual-run-api-errors";

export const usePostResolveData = (
  projectKey: string,
  runId: string,
): UseMutationResult<ResolvedData, ApiError, ResolveDataRequest> => {
  const apiErrors = useManualRunApiErrors();

  return useAppMutation<ResolvedData, ResolveDataRequest>({
    gcTime: 0,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/runs/{run_id}/resolve-data", {
          params: { path: { project_key: projectKey, run_id: runId } },
          body,
        }),
      );
    },
    apiErrors,
  });
};
