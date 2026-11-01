"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { CreateManualRunRequest, ManualRunCreated } from "../../typing/types/manual-run.type";
import { useManualRunApiErrors } from "../use-manual-run-api-errors";

export const usePostManualRun = (
  projectKey: string,
): UseMutationResult<ManualRunCreated, ApiError, CreateManualRunRequest> => {
  const apiErrors = useManualRunApiErrors();

  return useAppMutation<ManualRunCreated, CreateManualRunRequest>({
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/runs", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
    apiErrors,
    isGlobalErrorToastDisabled: true,
  });
};
