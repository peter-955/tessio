"use client";

import { DSButtonLink, DSEmptyState } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";

export const ProjectNotFound: FC = () => {
  const { t } = useTranslation("errors");

  return (
    <DSEmptyState
      icon="alertCircle"
      title={t("projectNotFound.title")}
      description={t("projectNotFound.message")}
      action={
        <DSButtonLink href="/projects" type="primary">
          {t("projectNotFound.backLink")}
        </DSButtonLink>
      }
    />
  );
};
