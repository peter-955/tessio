import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import type { QueryClient } from "@tanstack/react-query";
import { renderHook, type RenderHookResult } from "@testing-library/react";
import type { ReactNode } from "react";

type Result<HookResult> = RenderHookResult<HookResult, unknown> & { queryClient: QueryClient };

export const renderHookWithClient = <HookResult,>(hook: () => HookResult): Result<HookResult> => {
  const queryClient = createTestQueryClient();
  const result = renderHook(hook, {
    wrapper: ({ children }: { children: ReactNode }) => {
      return <TestProviders queryClient={queryClient}>{children}</TestProviders>;
    },
  });

  return { ...result, queryClient };
};
