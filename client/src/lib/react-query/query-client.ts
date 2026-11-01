import { QueryClient } from "@tanstack/react-query";
import { QUERY_STALE_TIME_IN_MILLISECONDS } from "./typing/constants/query-client.constant";

let browserQueryClient: QueryClient | undefined;

export const createQueryClient = (): QueryClient => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        refetchOnWindowFocus: false,
        staleTime: QUERY_STALE_TIME_IN_MILLISECONDS,
      },
      mutations: {
        retry: false,
      },
    },
  });
};

export const getOrCreateQueryClient = (): QueryClient => {
  if (typeof window === "undefined") {
    return createQueryClient();
  }

  browserQueryClient ??= createQueryClient();

  return browserQueryClient;
};
