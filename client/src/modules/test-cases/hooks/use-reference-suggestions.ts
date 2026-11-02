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
    const descriptionByKey = new Map<string, string | undefined>();
    (data ?? []).forEach((item) => {
      descriptionByKey.set(
        item.key,
        descriptionByKey.get(item.key) ?? item.description ?? undefined,
      );
    });
    const dataKeys = [...descriptionByKey.keys()].sort();
    const fileKeys = files.map((file) => file.key).sort();

    return [
      ...dataKeys.map((key): DSReferenceSuggestion => {
        const description = descriptionByKey.get(key);
        return description === undefined
          ? { kind: "data", key }
          : { kind: "data", key, description };
      }),
      ...fileKeys.map((key): DSReferenceSuggestion => ({ kind: "file", key })),
    ];
  }, [data, files]);
};
