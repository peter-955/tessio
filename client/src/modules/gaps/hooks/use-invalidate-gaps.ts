"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import { GET_GAP_INBOX_KEY } from "./queries/use-get-gap-inbox";
import { GET_STORY_GAPS_KEY } from "./queries/use-get-story-gaps";

export const useInvalidateGaps = (): (() => Promise<void>) => {
  const queryClient = useQueryClient();

  return useCallback(async (): Promise<void> => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: [GET_STORY_GAPS_KEY] }),
      queryClient.invalidateQueries({ queryKey: [GET_GAP_INBOX_KEY] }),
    ]);
  }, [queryClient]);
};
