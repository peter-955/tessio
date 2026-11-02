"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import type { DataItem } from "@/modules/test-data/typing/types/data-item.type";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";

export const GET_EFFECTIVE_TEST_DATA_KEY = "GET_EFFECTIVE_TEST_DATA_KEY";

export type GetEffectiveTestDataQueryKey = [
  typeof GET_EFFECTIVE_TEST_DATA_KEY,
  string,
  string | null,
];

type Result = Pick<UseQueryResult<DataItem[], ApiError>, "data" | "isPending">;

export const useGetEffectiveTestData = (
  projectKey: string,
  environmentId: string | null,
): Result => {
  const { data, isPending } = useAppQuery<DataItem[], GetEffectiveTestDataQueryKey>({
    queryKey: [GET_EFFECTIVE_TEST_DATA_KEY, projectKey, environmentId],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/test-data/effective", {
          params: { path: { project_key: projectKey }, query: { environmentId } },
          signal,
        }),
      );
    },
  });

  return { data, isPending };
};
