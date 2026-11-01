"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { UseMutationResult } from "@tanstack/react-query";
import { INLINE_RAISE_ERROR_CODES } from "../../typing/constants/gap-error.constant";
import type { Gap, RaiseGapBody } from "../../typing/types/gap.type";
import { useGapApiErrors } from "../use-gap-api-errors";
import { useInvalidateGaps } from "../use-invalidate-gaps";

export const usePostGap = (
  projectKey: string,
  storyKey: string,
): UseMutationResult<Gap, ApiError, RaiseGapBody> => {
  const invalidateGaps = useInvalidateGaps();
  const { showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useGapApiErrors();

  return useAppMutation<Gap, RaiseGapBody>({
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/stories/{jira_key}/gaps", {
          params: { path: { project_key: projectKey, jira_key: storyKey } },
          body,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
    onError: (error) => {
      if (error.code === null || !INLINE_RAISE_ERROR_CODES.has(error.code)) {
        showErrorToast(resolveMessage(error, apiErrors));
      }
    },
    onSettled: () => {
      return invalidateGaps();
    },
  });
};
