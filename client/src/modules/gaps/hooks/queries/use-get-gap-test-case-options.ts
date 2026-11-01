"use client";

import type { DSSelectOption } from "@/components/design-system";
import { apiClient } from "@/lib/api/api-client";
import type { components } from "@/lib/api/openapi.type";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { useMemo } from "react";
import { buildTestCaseOption } from "../../utils/target-options.util";

export const GET_GAP_TEST_CASE_OPTIONS_KEY = "GET_GAP_TEST_CASE_OPTIONS_KEY";

export type GetGapTestCaseOptionsQueryKey = [typeof GET_GAP_TEST_CASE_OPTIONS_KEY, string, string];

type TestCaseSummary = components["schemas"]["TestCaseSummaryResponse"];

interface Result {
  options: DSSelectOption<string>[];
  isPending: boolean;
  isError: boolean;
}

export const useGetGapTestCaseOptions = (
  projectKey: string,
  storyKey: string,
  isEnabled: boolean,
): Result => {
  const { data, isPending, isError } = useAppQuery<
    TestCaseSummary[],
    GetGapTestCaseOptionsQueryKey
  >({
    queryKey: [GET_GAP_TEST_CASE_OPTIONS_KEY, projectKey, storyKey],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/test-cases", {
          params: { path: { project_key: projectKey }, query: { storyKey } },
          signal,
        }),
      );
    },
    enabled: isEnabled,
  });

  const options = useMemo((): DSSelectOption<string>[] => {
    return (data ?? []).map((testCase): DSSelectOption<string> => {
      return buildTestCaseOption(testCase.code, testCase.title);
    });
  }, [data]);

  return { options, isPending: isEnabled && isPending, isError };
};
