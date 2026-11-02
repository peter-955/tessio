"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import type { SuiteDetail } from "../typing/types/suite.type";
import { GET_SUITE_KEY, type GetSuiteQueryKey } from "./queries/use-get-suite";
import { GET_SUITES_KEY } from "./queries/use-get-suites";

export const useStoreSuite = (projectKey: string): ((suite: SuiteDetail) => Promise<void>) => {
  const queryClient = useQueryClient();

  return useCallback(
    async (suite: SuiteDetail): Promise<void> => {
      const queryKey: GetSuiteQueryKey = [GET_SUITE_KEY, projectKey, suite.id];
      queryClient.setQueryData<SuiteDetail>(queryKey, suite);
      await queryClient.invalidateQueries({ queryKey: [GET_SUITES_KEY, projectKey] });
    },
    [projectKey, queryClient],
  );
};
