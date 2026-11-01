import { TestProviders } from "@/test/test-providers";
import type { QueryClient } from "@tanstack/react-query";
import type { FC, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

export const createProvidersWrapper = (queryClient: QueryClient): FC<Props> => {
  const ProvidersWrapper: FC<Props> = ({ children }) => {
    return <TestProviders queryClient={queryClient}>{children}</TestProviders>;
  };

  return ProvidersWrapper;
};
