import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import type { QueryClient } from "@tanstack/react-query";
import { render, type RenderResult } from "@testing-library/react";
import type { ReactElement } from "react";

interface Result extends RenderResult {
  queryClient: QueryClient;
}

export const renderWithProviders = (
  element: ReactElement,
  queryClient: QueryClient = createTestQueryClient(),
): Result => {
  const result = render(<TestProviders queryClient={queryClient}>{element}</TestProviders>);

  return { ...result, queryClient };
};
