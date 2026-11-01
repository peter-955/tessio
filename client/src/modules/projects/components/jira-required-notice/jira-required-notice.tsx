"use client";

import { DSButtonLink, DSEmptyState } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { WORKSPACE_SETTINGS_PATH } from "../../typing/constants/project-path.constant";

export const JiraRequiredNotice: FC = () => {
  const { t } = useTranslation("projects");

  return (
    <DSEmptyState
      title={t("create.jiraRequired.title")}
      description={t("create.jiraRequired.description")}
      icon="settings"
      action={
        <DSButtonLink href={WORKSPACE_SETTINGS_PATH} type="primary" hasArrow>
          {t("create.jiraRequired.action")}
        </DSButtonLink>
      }
    />
  );
};
