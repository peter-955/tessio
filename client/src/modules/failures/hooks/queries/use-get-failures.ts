"use client";

import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { keepPreviousData, type UseQueryResult } from "@tanstack/react-query";
import type {
  FailureAssigneeFilter,
  FailureFilters,
  FailureStatusFilter,
} from "../../typing/types/failure-filters.type";
import type { Failure } from "../../typing/types/failure.type";
import { buildFailureListQuery } from "../../utils/failure-filters.util";

export const GET_FAILURES_KEY = "GET_FAILURES_KEY";

export type GetFailuresQueryKey = [
  typeof GET_FAILURES_KEY,
  string,
  FailureStatusFilter,
  FailureAssigneeFilter,
  string | null,
];

type Result = Pick<
  UseQueryResult<Failure[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetFailures = (projectKey: string, filters: FailureFilters): Result => {
  const currentUser = useCurrentUser();
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    Failure[],
    GetFailuresQueryKey
  >({
    queryKey: [GET_FAILURES_KEY, projectKey, filters.status, filters.assignee, filters.storyKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/failures", {
          params: {
            path: { project_key: projectKey },
            query: buildFailureListQuery(filters, currentUser.id),
          },
          signal,
        }),
      );
    },
    placeholderData: keepPreviousData,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
