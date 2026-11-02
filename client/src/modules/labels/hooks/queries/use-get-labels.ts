"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { Label } from "../../typing/types/label.type";

export const GET_LABELS_KEY = "GET_LABELS_KEY";

export type GetLabelsQueryKey = [typeof GET_LABELS_KEY, string];

type Result = Pick<
  UseQueryResult<Label[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetLabels = (projectKey: string, isEnabled = true): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    Label[],
    GetLabelsQueryKey
  >({
    queryKey: [GET_LABELS_KEY, projectKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/labels", {
          params: { path: { project_key: projectKey } },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
