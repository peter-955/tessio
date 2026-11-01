import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import type { QueryClient } from "@tanstack/react-query";
import { render, type RenderResult } from "@testing-library/react";
import { StrictMode, type ReactElement } from "react";

interface Options {
  queryClient?: QueryClient;
  isStrictMode?: boolean;
}

interface Result extends RenderResult {
  queryClient: QueryClient;
}

export const renderWithProviders = (
  element: ReactElement,
  { queryClient = createTestQueryClient(), isStrictMode = false }: Options = {},
): Result => {
  const providedElement = <TestProviders queryClient={queryClient}>{element}</TestProviders>;
  const result = render(
    isStrictMode ? <StrictMode>{providedElement}</StrictMode> : providedElement,
  );

  return { ...result, queryClient };
};
