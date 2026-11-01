"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { FILE_LINK_STALE_TIME_IN_MILLISECONDS } from "../../typing/constants/run.constant";
import type { FileLink } from "../../typing/types/run.type";

export const GET_RUN_FILE_LINK_KEY = "GET_RUN_FILE_LINK_KEY";

export type GetRunFileLinkQueryKey = [typeof GET_RUN_FILE_LINK_KEY, string, string];

type Result = Pick<UseQueryResult<FileLink, ApiError>, "data" | "isPending" | "isError">;

export const useGetFileLink = (projectKey: string, fileId: string): Result => {
  const { data, isPending, isError } = useAppQuery<FileLink, GetRunFileLinkQueryKey>({
    queryKey: [GET_RUN_FILE_LINK_KEY, projectKey, fileId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/files/{file_id}", {
          params: { path: { project_key: projectKey, file_id: fileId } },
          signal,
        }),
      );
    },
    staleTime: FILE_LINK_STALE_TIME_IN_MILLISECONDS,
    retry: false,
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError };
};
