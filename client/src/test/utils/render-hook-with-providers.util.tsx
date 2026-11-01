import type { QueryClient } from "@tanstack/react-query";
import { renderHook, type RenderHookResult } from "@testing-library/react";
import type { ReactNode } from "react";
import { TestProviders } from "../test-providers";
import { createTestQueryClient } from "./create-test-query-client.util";

interface Result<HookResult> {
  result: RenderHookResult<HookResult, unknown>["result"];
  queryClient: QueryClient;
}

export const renderHookWithProviders = <HookResult,>(
  hook: () => HookResult,
): Result<HookResult> => {
  const queryClient = createTestQueryClient();
  const { result } = renderHook(hook, {
    wrapper: ({ children }: { children: ReactNode }) => {
      return <TestProviders queryClient={queryClient}>{children}</TestProviders>;
    },
  });

  return { result, queryClient };
};
