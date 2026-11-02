"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { ChangeFailureCauseRequest, Failure } from "../../typing/types/failure.type";
import { useFailureApiErrors } from "../use-failure-api-errors";
import { useInvalidateFailures } from "../use-invalidate-failures";

export const usePutFailureCause = (
  projectKey: string,
  failureId: string,
): UseMutationResult<Failure, ApiError, ChangeFailureCauseRequest> => {
  const invalidateFailures = useInvalidateFailures();
  const apiErrors = useFailureApiErrors();

  return useAppMutation<Failure, ChangeFailureCauseRequest>({
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.PUT("/api/projects/{project_key}/failures/{failure_id}/cause", {
          params: { path: { project_key: projectKey, failure_id: failureId } },
          body,
        }),
      );
    },
    apiErrors,
    onSettled: () => {
      return invalidateFailures();
    },
  });
};
