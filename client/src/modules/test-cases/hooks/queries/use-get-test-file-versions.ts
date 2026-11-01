"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { TestFileVersion } from "../../typing/types/test-case.type";

export const GET_TEST_FILE_VERSIONS_KEY = "GET_TEST_FILE_VERSIONS_KEY";

export type GetTestFileVersionsQueryKey = [
  typeof GET_TEST_FILE_VERSIONS_KEY,
  string,
  string,
  string,
];

type Result = Pick<
  UseQueryResult<TestFileVersion[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetTestFileVersions = (
  projectKey: string,
  caseCode: string,
  fileKey: string,
  isEnabled: boolean,
): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    TestFileVersion[],
    GetTestFileVersionsQueryKey
  >({
    queryKey: [GET_TEST_FILE_VERSIONS_KEY, projectKey, caseCode, fileKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET(
          "/api/projects/{project_key}/test-cases/{case_code}/files/{file_key}/versions",
          {
            params: { path: { project_key: projectKey, case_code: caseCode, file_key: fileKey } },
            signal,
          },
        ),
      );
    },
    enabled: isEnabled,
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
