"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { Gap } from "../../typing/types/gap.type";

export const GET_GAP_INBOX_KEY = "GET_GAP_INBOX_KEY";

export type GetGapInboxQueryKey = [typeof GET_GAP_INBOX_KEY, { isIncludingResolved: boolean }];

type Result = Pick<
  UseQueryResult<Gap[], ApiError>,
  "data" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetGapInbox = (isIncludingResolved: boolean): Result => {
  const { data, isPending, isError, isFetching, refetch } = useAppQuery<Gap[], GetGapInboxQueryKey>(
    {
      queryKey: [GET_GAP_INBOX_KEY, { isIncludingResolved }],
      queryFn: ({ signal }) => {
        return unwrapResponse(
          apiClient.GET("/api/gaps/inbox", {
            params: { query: { includeResolved: isIncludingResolved } },
            signal,
          }),
        );
      },
      isGlobalErrorToastDisabled: true,
    },
  );

  return { data, isPending, isError, isFetching, refetch };
};
