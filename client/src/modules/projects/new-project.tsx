"use client";

import { DSEmptyState, DSPageHeader } from "@/components/design-system";
import { useGetJiraConnection } from "@/modules/settings/hooks/queries/use-get-jira-connection";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { CreateProjectForm } from "./components/create-project-form/create-project-form";
import { JiraLoadError } from "./components/jira-load-error/jira-load-error";
import { JiraRequiredNotice } from "./components/jira-required-notice/jira-required-notice";
import { LoadingState } from "./components/loading-state/loading-state";
import { useGetJiraProjects } from "./hooks/queries/use-get-jira-projects";
import { useIsWorkspaceAdmin } from "./hooks/use-is-workspace-admin";

export const NewProjectPage: FC = () => {
  const { t } = useTranslation("projects");
  const isWorkspaceAdmin = useIsWorkspaceAdmin();
  const connection = useGetJiraConnection({ isEnabled: isWorkspaceAdmin });
  const isConfigured = connection.data?.isConfigured === true;
  const jiraProjects = useGetJiraProjects({ isEnabled: isWorkspaceAdmin && isConfigured });
  const isJiraNotConfigured =
    connection.data?.isConfigured === false || jiraProjects.error?.code === "JIRA_NOT_CONFIGURED";

  const renderContent = (): ReactNode => {
    if (!isWorkspaceAdmin) {
      return <DSEmptyState title={t("create.adminOnly")} icon="lock" />;
    }

    if (connection.isPending) {
      return <LoadingState label={t("create.loading")} />;
    }

    if (connection.error) {
      return (
        <JiraLoadError
          error={connection.error}
          isRetrying={connection.isFetching}
          onRetry={() => {
            void connection.refetch();
          }}
        />
      );
    }

    if (isJiraNotConfigured) {
      return <JiraRequiredNotice />;
    }

    if (jiraProjects.isPending) {
      return <LoadingState label={t("create.loading")} />;
    }

    if (jiraProjects.error) {
      return (
        <JiraLoadError
          error={jiraProjects.error}
          isRetrying={jiraProjects.isFetching}
          onRetry={() => {
            void jiraProjects.refetch();
          }}
        />
      );
    }

    return (
      <CreateProjectForm
        jiraProjects={jiraProjects.data ?? []}
        onJiraProjectLinked={() => {
          void jiraProjects.refetch();
        }}
        onJiraNotConfigured={() => {
          void connection.refetch();
        }}
      />
    );
  };

  return (
    <>
      <DSPageHeader title={t("create.title")} description={t("create.description")} />
      {renderContent()}
    </>
  );
};
