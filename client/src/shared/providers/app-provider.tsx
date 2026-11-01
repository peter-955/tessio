"use client";

import "@/lib/dayjs/dayjs-locales";

import { DSToaster } from "@/components/design-system";
import { createI18nInstance } from "@/lib/i18n";
import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { getOrCreateQueryClient } from "@/lib/react-query/query-client";
import { MantineProvider } from "@mantine/core";
import { QueryClientProvider } from "@tanstack/react-query";
import { useState, type FC, type ReactNode } from "react";
import { I18nextProvider } from "react-i18next";
import type { Language } from "../typing/enums/language.enum";
import { LocaleProvider } from "./locale-provider";

interface Props {
  language: Language;
  children: ReactNode;
}

export const AppProvider: FC<Props> = ({ language, children }) => {
  const [i18n] = useState(() => {
    return createI18nInstance(language);
  });
  const [queryClient] = useState(() => {
    return getOrCreateQueryClient();
  });

  return (
    <I18nextProvider i18n={i18n}>
      <QueryClientProvider client={queryClient}>
        <MantineProvider theme={mantineTheme} defaultColorScheme="auto">
          <LocaleProvider>
            <DSToaster />
            {children}
          </LocaleProvider>
        </MantineProvider>
      </QueryClientProvider>
    </I18nextProvider>
  );
};
