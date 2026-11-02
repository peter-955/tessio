"use client";

import { DSButtonLink, DSEmptyState } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { buildSuitesPath } from "../../utils/suite-path.util";

interface Props {
  projectKey: string;
}

export const SuiteNotFound: FC<Props> = ({ projectKey }) => {
  const { t } = useTranslation("suites");

  return (
    <DSEmptyState
      title={t("detail.notFoundTitle")}
      description={t("detail.notFoundDescription")}
      icon="suites"
      action={
        <DSButtonLink href={buildSuitesPath(projectKey)} type="default">
          {t("detail.back")}
        </DSButtonLink>
      }
    />
  );
};
