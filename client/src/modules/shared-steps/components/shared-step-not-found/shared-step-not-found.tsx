"use client";

import { DSButtonLink, DSEmptyState } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { buildSharedStepsPath } from "../../utils/shared-step-path.util";

interface Props {
  projectKey: string;
}

export const SharedStepNotFound: FC<Props> = ({ projectKey }) => {
  const { t } = useTranslation("sharedSteps");

  return (
    <DSEmptyState
      title={t("detail.notFoundTitle")}
      description={t("detail.notFoundDescription")}
      icon="sharedSteps"
      action={
        <DSButtonLink href={buildSharedStepsPath(projectKey)} type="default">
          {t("detail.back")}
        </DSButtonLink>
      }
    />
  );
};
