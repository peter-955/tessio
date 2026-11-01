"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { GapReference } from "../../typing/types/gap-mutation-variables.type";
import type { Gap } from "../../typing/types/gap.type";
import { useGapApiErrors } from "../use-gap-api-errors";
import { useInvalidateGaps } from "../use-invalidate-gaps";

export const usePostGapReopen = (): UseMutationResult<Gap, ApiError, GapReference> => {
  const invalidateGaps = useInvalidateGaps();
  const apiErrors = useGapApiErrors();

  return useAppMutation<Gap, GapReference>({
    mutationFn: ({ projectKey, gapId }) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/gaps/{gap_id}/reopen", {
          params: { path: { project_key: projectKey, gap_id: gapId } },
        }),
      );
    },
    apiErrors,
    onSettled: () => {
      return invalidateGaps();
    },
  });
};
