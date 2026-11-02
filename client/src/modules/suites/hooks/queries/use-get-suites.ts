"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { keepPreviousData, type UseQueryResult } from "@tanstack/react-query";
import type { SuiteSummary } from "../../typing/types/suite.type";

export const GET_SUITES_KEY = "GET_SUITES_KEY";

export type GetSuitesQueryKey = [typeof GET_SUITES_KEY, string, boolean];

type Result = Pick<
  UseQueryResult<SuiteSummary[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetSuites = (
  projectKey: string,
  isArchivedShown = false,
  isEnabled = true,
): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    SuiteSummary[],
    GetSuitesQueryKey
  >({
    queryKey: [GET_SUITES_KEY, projectKey, isArchivedShown],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/suites", {
          params: {
            path: { project_key: projectKey },
            query: isArchivedShown ? { archived: true } : {},
          },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    placeholderData: keepPreviousData,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
