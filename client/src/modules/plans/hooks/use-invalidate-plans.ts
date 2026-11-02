"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import { GET_PLAN_KEY } from "./queries/use-get-plan";
import { GET_PLANS_KEY } from "./queries/use-get-plans";

export const useInvalidatePlans = (): (() => Promise<void>) => {
  const queryClient = useQueryClient();

  return useCallback(async (): Promise<void> => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: [GET_PLANS_KEY] }),
      queryClient.invalidateQueries({ queryKey: [GET_PLAN_KEY] }),
    ]);
  }, [queryClient]);
};
