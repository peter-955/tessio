"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { AnswerGapVariables } from "../../typing/types/gap-mutation-variables.type";
import type { Gap } from "../../typing/types/gap.type";
import { useGapApiErrors } from "../use-gap-api-errors";
import { useInvalidateGaps } from "../use-invalidate-gaps";

export const usePutGapAnswer = (): UseMutationResult<Gap, ApiError, AnswerGapVariables> => {
  const invalidateGaps = useInvalidateGaps();
  const apiErrors = useGapApiErrors();

  return useAppMutation<Gap, AnswerGapVariables>({
    mutationFn: ({ projectKey, gapId, answer }) => {
      return unwrapResponse(
        apiClient.PUT("/api/projects/{project_key}/gaps/{gap_id}/answer", {
          params: { path: { project_key: projectKey, gap_id: gapId } },
          body: { answer },
        }),
      );
    },
    apiErrors,
    onSettled: () => {
      return invalidateGaps();
    },
  });
};
