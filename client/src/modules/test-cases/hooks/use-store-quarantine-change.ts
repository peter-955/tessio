"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import type { TestCaseDetail } from "../typing/types/test-case.type";
import { GET_CASE_LATEST_RESULTS_KEY } from "./queries/use-get-case-latest-results";
import { GET_QUARANTINE_EVENTS_KEY } from "./queries/use-get-quarantine-events";
import { useStoreTestCaseDetail } from "./use-store-test-case-detail";

export const useStoreQuarantineChange = (
  projectKey: string,
): ((detail: TestCaseDetail) => Promise<void>) => {
  const queryClient = useQueryClient();
  const storeDetail = useStoreTestCaseDetail(projectKey);

  return useCallback(
    async (detail: TestCaseDetail): Promise<void> => {
      await Promise.all([
        storeDetail(detail),
        queryClient.invalidateQueries({ queryKey: [GET_CASE_LATEST_RESULTS_KEY, projectKey] }),
        queryClient.invalidateQueries({
          queryKey: [GET_QUARANTINE_EVENTS_KEY, projectKey, detail.code],
        }),
      ]);
    },
    [projectKey, queryClient, storeDetail],
  );
};
