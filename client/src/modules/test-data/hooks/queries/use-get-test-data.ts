"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { DataItem } from "../../typing/types/data-item.type";

export const GET_TEST_DATA_KEY = "GET_TEST_DATA_KEY";

export type GetTestDataQueryKey = [typeof GET_TEST_DATA_KEY, string];

type Result = Pick<
  UseQueryResult<DataItem[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetTestData = (projectKey: string): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    DataItem[],
    GetTestDataQueryKey
  >({
    queryKey: [GET_TEST_DATA_KEY, projectKey],
    queryFn: () => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/test-data", {
          params: { path: { project_key: projectKey } },
        }),
      );
    },
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
