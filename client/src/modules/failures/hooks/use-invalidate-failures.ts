"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import { GET_FAILURE_KEY } from "./queries/use-get-failure";
import { GET_FAILURES_KEY } from "./queries/use-get-failures";

export const useInvalidateFailures = (): (() => Promise<void>) => {
  const queryClient = useQueryClient();

  return useCallback(async (): Promise<void> => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: [GET_FAILURES_KEY] }),
      queryClient.invalidateQueries({ queryKey: [GET_FAILURE_KEY] }),
    ]);
  }, [queryClient]);
};
