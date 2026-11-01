"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { UseMutationResult } from "@tanstack/react-query";
import { INLINE_REASSIGN_ERROR_CODES } from "../../typing/constants/gap-error.constant";
import type { ReassignGapVariables } from "../../typing/types/gap-mutation-variables.type";
import type { Gap } from "../../typing/types/gap.type";
import { useGapApiErrors } from "../use-gap-api-errors";
import { useInvalidateGaps } from "../use-invalidate-gaps";

export const usePutGapAssignee = (): UseMutationResult<Gap, ApiError, ReassignGapVariables> => {
  const invalidateGaps = useInvalidateGaps();
  const { showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useGapApiErrors();

  return useAppMutation<Gap, ReassignGapVariables>({
    mutationFn: ({ projectKey, gapId, body }) => {
      return unwrapResponse(
        apiClient.PUT("/api/projects/{project_key}/gaps/{gap_id}/assignee", {
          params: { path: { project_key: projectKey, gap_id: gapId } },
          body,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
    onError: (error) => {
      if (error.code === null || !INLINE_REASSIGN_ERROR_CODES.has(error.code)) {
        showErrorToast(resolveMessage(error, apiErrors));
      }
    },
    onSettled: () => {
      return invalidateGaps();
    },
  });
};
