"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import type { TestCaseDetail } from "../typing/types/test-case.type";
import { GET_TEST_CASE_KEY, type GetTestCaseQueryKey } from "./queries/use-get-test-case";
import { GET_TEST_CASE_VERSIONS_KEY } from "./queries/use-get-test-case-versions";
import { GET_TEST_CASES_KEY } from "./queries/use-get-test-cases";
import { GET_TEST_FILE_VERSIONS_KEY } from "./queries/use-get-test-file-versions";

export const useStoreTestCaseDetail = (
  projectKey: string,
): ((detail: TestCaseDetail, isFileChanged?: boolean) => Promise<void>) => {
  const queryClient = useQueryClient();

  return useCallback(
    async (detail: TestCaseDetail, isFileChanged = false): Promise<void> => {
      const queryKey: GetTestCaseQueryKey = [GET_TEST_CASE_KEY, projectKey, detail.code];
      queryClient.setQueryData(queryKey, detail);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: [GET_TEST_CASES_KEY] }),
        queryClient.invalidateQueries({
          queryKey: [GET_TEST_CASE_VERSIONS_KEY, projectKey, detail.code],
        }),
        ...(isFileChanged
          ? [
              queryClient.invalidateQueries({
                queryKey: [GET_TEST_FILE_VERSIONS_KEY, projectKey, detail.code],
              }),
            ]
          : []),
      ]);
    },
    [projectKey, queryClient],
  );
};
