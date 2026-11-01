"use client";

import { DatesProvider } from "@mantine/dates";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useSyncDocumentLanguage } from "../hooks/use-sync-document-language";

interface Props {
  children: ReactNode;
}

export const LocaleProvider: FC<Props> = ({ children }) => {
  const { i18n } = useTranslation();
  useSyncDocumentLanguage(i18n.language);

  return <DatesProvider settings={{ locale: i18n.language }}>{children}</DatesProvider>;
};
