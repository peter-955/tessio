"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import { SCREENSHOT_LINK_STALE_MILLISECONDS } from "../../typing/constants/failure.constant";
import type { DownloadLink } from "../../typing/types/failure.type";

export const GET_FAILURE_SCREENSHOT_LINK_KEY = "GET_FAILURE_SCREENSHOT_LINK_KEY";

export type GetFailureScreenshotLinkQueryKey = [
  typeof GET_FAILURE_SCREENSHOT_LINK_KEY,
  string,
  string,
];

type Result = Pick<UseQueryResult<DownloadLink, ApiError>, "data" | "isPending" | "isError">;

export const useGetScreenshotLink = (
  projectKey: string,
  fileId: string,
  isEnabled: boolean,
): Result => {
  const { data, isPending, isError } = useAppQuery<DownloadLink, GetFailureScreenshotLinkQueryKey>({
    queryKey: [GET_FAILURE_SCREENSHOT_LINK_KEY, projectKey, fileId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/files/{file_id}", {
          params: { path: { project_key: projectKey, file_id: fileId } },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    staleTime: SCREENSHOT_LINK_STALE_MILLISECONDS,
    retry: false,
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError };
};
