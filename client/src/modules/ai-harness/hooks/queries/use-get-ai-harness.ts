"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { AiHarness } from "../../typing/types/ai-harness.type";

export const GET_AI_HARNESS_KEY = "GET_AI_HARNESS_KEY";

type GetAiHarnessKey = [typeof GET_AI_HARNESS_KEY];

type Result = Pick<
  UseQueryResult<AiHarness, ApiError>,
  "data" | "isPending" | "isError" | "refetch" | "isRefetching"
>;

export const useGetAiHarness = (): Result => {
  const { data, isPending, isError, refetch, isRefetching } = useAppQuery<
    AiHarness,
    GetAiHarnessKey
  >({
    queryKey: [GET_AI_HARNESS_KEY],
    queryFn: ({ signal }) => {
      return unwrapResponse(apiClient.GET("/api/ai-harness", { signal }));
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError, refetch, isRefetching };
};
