import { AppProvider } from "@/shared/providers/app-provider";
import { Language } from "@/shared/typing/enums/language.enum";
import { QueryClientProvider, type QueryClient } from "@tanstack/react-query";
import type { FC, ReactNode } from "react";

interface Props {
  queryClient: QueryClient;
  children: ReactNode;
}

export const TestProviders: FC<Props> = ({ queryClient, children }) => {
  return (
    <AppProvider language={Language.ENGLISH}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </AppProvider>
  );
};
