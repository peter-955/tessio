"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { SYNC_STATUS_POLL_INTERVAL_IN_MILLISECONDS } from "../../typing/constants/sync.constant";
import type { ProjectSyncState } from "../../typing/types/story.type";
import { checkIsSyncInProgress } from "../../utils/sync-status.util";

export const GET_SYNC_STATUS_KEY = "GET_SYNC_STATUS_KEY";

export type GetSyncStatusQueryKey = [typeof GET_SYNC_STATUS_KEY, string];

type Result = Pick<
  UseQueryResult<ProjectSyncState, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch" | "dataUpdatedAt"
>;

export const useGetSyncStatus = (projectKey: string): Result => {
  const { data, error, isPending, isError, isFetching, refetch, dataUpdatedAt } = useAppQuery<
    ProjectSyncState,
    GetSyncStatusQueryKey
  >({
    queryKey: [GET_SYNC_STATUS_KEY, projectKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/sync", {
          params: { path: { project_key: projectKey } },
          signal,
        }),
      );
    },
    refetchInterval: (query) => {
      return checkIsSyncInProgress(query.state.data, new Date())
        ? SYNC_STATUS_POLL_INTERVAL_IN_MILLISECONDS
        : false;
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch, dataUpdatedAt };
};
