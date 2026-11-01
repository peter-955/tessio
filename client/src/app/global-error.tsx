"use client";

import "@/shared/styles/globals.scss";
import "@mantine/core/styles.layer.css";
import "@mantine/dates/styles.layer.css";
import "@mantine/dropzone/styles.layer.css";

import { DS_HTML_ATTRIBUTES } from "@/components/design-system";
import { ErrorPage } from "@/modules/errors/error-page";
import { useDocumentLanguage } from "@/modules/errors/hooks/use-document-language";
import { AppProvider } from "@/shared/providers/app-provider";
import type { FC } from "react";

interface Props {
  error: unknown;
  retry: () => void;
}

const GlobalErrorRoute: FC<Props> = ({ error, retry }) => {
  const language = useDocumentLanguage();

  return (
    <html lang={language} {...DS_HTML_ATTRIBUTES}>
      <body>
        <title>Tessio</title>
        <AppProvider key={language} language={language}>
          <ErrorPage error={error} onRetry={retry} />
        </AppProvider>
      </body>
    </html>
  );
};

export default GlobalErrorRoute;
