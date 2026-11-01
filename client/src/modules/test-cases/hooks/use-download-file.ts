"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { DownloadLink } from "../typing/types/test-case.type";

const NEW_TAB_TARGET = "_blank";

const NEW_TAB_FEATURES = "noopener";

export const useDownloadFile = (
  projectKey: string,
): UseMutationResult<DownloadLink, ApiError, string> => {
  return useAppMutation<DownloadLink, string>({
    mutationFn: (fileId) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/files/{file_id}", {
          params: { path: { project_key: projectKey, file_id: fileId } },
        }),
      );
    },
    onSuccess: (link) => {
      window.open(link.url, NEW_TAB_TARGET, NEW_TAB_FEATURES);
    },
  });
};
