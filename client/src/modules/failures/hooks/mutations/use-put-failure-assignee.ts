"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { UseMutationResult } from "@tanstack/react-query";
import type { Failure } from "../../typing/types/failure.type";
import { useFailureApiErrors } from "../use-failure-api-errors";
import { useInvalidateFailures } from "../use-invalidate-failures";

export const usePutFailureAssignee = (
  projectKey: string,
  failureId: string,
): UseMutationResult<Failure, ApiError, string | null> => {
  const invalidateFailures = useInvalidateFailures();
  const { showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useFailureApiErrors();

  return useAppMutation<Failure, string | null>({
    mutationFn: (assigneeId) => {
      return unwrapResponse(
        apiClient.PUT("/api/projects/{project_key}/failures/{failure_id}/assignee", {
          params: { path: { project_key: projectKey, failure_id: failureId } },
          body: { assigneeId },
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
    onError: (error) => {
      if (error.code !== "ASSIGNEE_NOT_ACTIVE_MEMBER") {
        showErrorToast(resolveMessage(error, apiErrors));
      }
    },
    onSettled: () => {
      return invalidateFailures();
    },
  });
};
