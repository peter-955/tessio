"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { QuarantineEvent } from "../../typing/types/quarantine.type";

export const GET_QUARANTINE_EVENTS_KEY = "GET_QUARANTINE_EVENTS_KEY";

export type GetQuarantineEventsQueryKey = [typeof GET_QUARANTINE_EVENTS_KEY, string, string];

type Result = Pick<
  UseQueryResult<QuarantineEvent[], ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetQuarantineEvents = (projectKey: string, caseCode: string): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<
    QuarantineEvent[],
    GetQuarantineEventsQueryKey
  >({
    queryKey: [GET_QUARANTINE_EVENTS_KEY, projectKey, caseCode],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/test-cases/{case_code}/quarantine-events", {
          params: { path: { project_key: projectKey, case_code: caseCode } },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, isPending, isError, isFetching, refetch };
};
