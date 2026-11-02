"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { NEW_TAB_FEATURES, NEW_TAB_TARGET } from "../../typing/constants/report.constant";
import type { ReportDownloadLink } from "../../typing/types/report.type";

interface Variables {
  projectKey: string;
  fileId: string;
}

export const useDownloadReport = (): UseMutationResult<ReportDownloadLink, ApiError, Variables> => {
  const { t } = useTranslation("reports");

  return useAppMutation<ReportDownloadLink, Variables>({
    mutationFn: ({ projectKey, fileId }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/files/{file_id}", {
          params: { path: { project_key: projectKey, file_id: fileId } },
        }),
      );
    },
    apiErrors: { NOT_FOUND: t("download.notFound") },
    onSuccess: (link) => {
      window.open(link.url, NEW_TAB_TARGET, NEW_TAB_FEATURES);
    },
  });
};
