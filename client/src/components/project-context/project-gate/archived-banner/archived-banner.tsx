"use client";

import { DSAlert } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";

export const ArchivedBanner: FC = () => {
  const { t } = useTranslation();

  return (
    <DSAlert color="warning" title={t("appShell.archivedBanner.title")}>
      {t("appShell.archivedBanner.message")}
    </DSAlert>
  );
};
