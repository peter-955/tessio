"use client";

import { DSButtonLink, DSEmptyState } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { buildRunsPath } from "../../utils/run-path.util";

interface Props {
  projectKey: string;
}

export const RunNotFound: FC<Props> = ({ projectKey }) => {
  const { t } = useTranslation("runs");

  return (
    <DSEmptyState
      title={t("notFound.title")}
      description={t("notFound.description")}
      icon="runs"
      action={
        <DSButtonLink href={buildRunsPath(projectKey)} type="default">
          {t("notFound.back")}
        </DSButtonLink>
      }
    />
  );
};
