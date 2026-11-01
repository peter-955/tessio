import { createQueryClient } from "@/lib/react-query/query-client";
import type { QueryClient } from "@tanstack/react-query";

export const createTestQueryClient = (): QueryClient => {
  const queryClient = createQueryClient();

  queryClient.setDefaultOptions({
    queries: { ...queryClient.getDefaultOptions().queries, gcTime: Infinity, retry: false },
    mutations: { ...queryClient.getDefaultOptions().mutations, gcTime: Infinity, retry: false },
  });

  return queryClient;
};
