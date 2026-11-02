"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import type { UseMutationResult } from "@tanstack/react-query";
import type { ReportExportTarget } from "../../typing/types/report-export-target.type";
import type { ReportExport, ReportFormat } from "../../typing/types/report.type";

interface Options {
  onSuccess?: (reportExport: ReportExport) => void;
}

const requestExport = (
  projectKey: string,
  target: ReportExportTarget,
  format: ReportFormat,
): Promise<ReportExport> => {
  const body = { format };

  switch (target.source) {
    case "run":
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/runs/{run_id}/export", {
          params: { path: { project_key: projectKey, run_id: target.runId } },
          body,
        }),
      );
    case "plan":
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/plans/{plan_id}/export", {
          params: { path: { project_key: projectKey, plan_id: target.planId } },
          body,
        }),
      );
    case "story":
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/stories/{jira_key}/export", {
          params: { path: { project_key: projectKey, jira_key: target.jiraKey } },
          body,
        }),
      );
    default:
      target satisfies never;
      return Promise.reject(new Error("Unknown report source"));
  }
};

export const usePostReportExport = (
  projectKey: string,
  target: ReportExportTarget,
  options: Options = {},
): UseMutationResult<ReportExport, ApiError, ReportFormat> => {
  return useAppMutation<ReportExport, ReportFormat>({
    mutationFn: (format) => {
      return requestExport(projectKey, target, format);
    },
    onSuccess: (reportExport) => {
      options.onSuccess?.(reportExport);
    },
  });
};
