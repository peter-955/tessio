"use client";

import { DSEmptyState, DSErrorState, DSPageHeader } from "@/components/design-system";
import { LoadingState } from "@/modules/projects/components/loading-state/loading-state";
import { useIsWorkspaceAdmin } from "@/modules/projects/hooks/use-is-workspace-admin";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { JiraConnectionCard } from "./components/jira-connection-card/jira-connection-card";
import { useGetJiraConnection } from "./hooks/queries/use-get-jira-connection";

export const WorkspaceSettingsPage: FC = () => {
  const { t } = useTranslation("settings");
  const isWorkspaceAdmin = useIsWorkspaceAdmin();
  const {
    data: connection,
    isPending,
    isError,
    isFetching,
    refetch,
  } = useGetJiraConnection({
    isEnabled: isWorkspaceAdmin,
  });

  const renderContent = (): ReactNode => {
    if (!isWorkspaceAdmin) {
      return <DSEmptyState title={t("adminOnly")} icon="lock" />;
    }

    if (isPending) {
      return <LoadingState label={t("jira.loading")} />;
    }

    if (isError || connection === undefined) {
      return (
        <DSErrorState
          title={t("jira.loadError")}
          retryLabel={t("jira.retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    return <JiraConnectionCard connection={connection} />;
  };

  return (
    <>
      <DSPageHeader title={t("title")} description={t("description")} />
      {renderContent()}
    </>
  );
};
