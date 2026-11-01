"use client";

import { DSAlert, DSButton, DSButtonLink, DSGroup } from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { WORKSPACE_SETTINGS_PATH } from "../../typing/constants/project-path.constant";

interface Props {
  error: ApiError;
  onRetry: () => void;
  isRetrying?: boolean;
}

export const JiraLoadError: FC<Props> = ({ error, onRetry, isRetrying = false }) => {
  const { t } = useTranslation("projects");
  const resolveMessage = useResolveApiErrorMessage();

  return (
    <DSAlert
      color="danger"
      title={t("errors.jiraLoadFailed")}
      action={
        <DSGroup gap={2} isWrapping>
          <DSButton type="default" icon="refresh" isLoading={isRetrying} onClick={onRetry}>
            {t("errors.retry")}
          </DSButton>
          <DSButtonLink href={WORKSPACE_SETTINGS_PATH} type="ghost" icon="settings">
            {t("errors.openJiraSettings")}
          </DSButtonLink>
        </DSGroup>
      }
    >
      {resolveMessage(error)}
    </DSAlert>
  );
};
