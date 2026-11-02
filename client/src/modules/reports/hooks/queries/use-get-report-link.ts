"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { ReportDownloadLink } from "../../typing/types/report.type";
import { pickReportLinkPollInterval } from "../../utils/report-link-poll.util";

export const GET_REPORT_LINK_KEY = "GET_REPORT_LINK_KEY";

export type GetReportLinkQueryKey = [typeof GET_REPORT_LINK_KEY, string, string];

type Result = Pick<
  UseQueryResult<ReportDownloadLink, ApiError>,
  "data" | "error" | "isError" | "errorUpdateCount"
>;

export const useGetReportLink = (
  projectKey: string,
  fileId: string,
  isEnabled: boolean,
): Result => {
  const { data, error, isError, errorUpdateCount } = useAppQuery<
    ReportDownloadLink,
    GetReportLinkQueryKey
  >({
    queryKey: [GET_REPORT_LINK_KEY, projectKey, fileId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/files/{file_id}", {
          params: { path: { project_key: projectKey, file_id: fileId } },
          signal,
        }),
      );
    },
    enabled: isEnabled,
    retry: false,
    refetchInterval: (query) => {
      return pickReportLinkPollInterval({
        hasLink: query.state.data !== undefined,
        failedPollCount: query.state.errorUpdateCount,
      });
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isError, errorUpdateCount };
};
