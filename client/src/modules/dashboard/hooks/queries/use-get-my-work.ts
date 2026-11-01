"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { MyWork } from "../../typing/types/my-work.type";

export const GET_MY_WORK_KEY = "GET_MY_WORK_KEY";

export type GetMyWorkQueryKey = [typeof GET_MY_WORK_KEY, string, string | null];

type Result = Pick<
  UseQueryResult<MyWork, ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetMyWork = (projectKey: string, sprintId: string | null): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    MyWork,
    GetMyWorkQueryKey
  >({
    queryKey: [GET_MY_WORK_KEY, projectKey, sprintId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/my-work", {
          params: {
            path: { project_key: projectKey },
            ...(sprintId === null ? {} : { query: { sprintId } }),
          },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
