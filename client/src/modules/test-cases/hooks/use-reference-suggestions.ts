"use client";

import type { DSReferenceSuggestion } from "@/components/design-system";
import { useGetTestData } from "@/modules/test-data/hooks/queries/use-get-test-data";
import { useMemo } from "react";
import type { TestFile } from "../typing/types/test-case.type";

export const useReferenceSuggestions = (
  projectKey: string,
  files: readonly TestFile[],
): DSReferenceSuggestion[] => {
  const { data } = useGetTestData(projectKey);

  return useMemo((): DSReferenceSuggestion[] => {
    const dataKeys = [...new Set((data ?? []).map((item) => item.key))].sort();
    const fileKeys = files.map((file) => file.key).sort();

    return [
      ...dataKeys.map((key): DSReferenceSuggestion => ({ kind: "data", key })),
      ...fileKeys.map((key): DSReferenceSuggestion => ({ kind: "file", key })),
    ];
  }, [data, files]);
};
