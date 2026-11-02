"use client";

import { DSEmptyState, DSErrorState, DSPageHeader, DSSkeleton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { SyncControl } from "@/modules/stories/components/sync-control/sync-control";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { SprintTable } from "./components/sprint-table/sprint-table";
import { useGetSprints } from "./hooks/queries/use-get-sprints";

export const SprintsPage: FC = () => {
  const { t } = useTranslation("sprints");
  const project = useCurrentProject();
  const { data, isPending, isError, isFetching, refetch } = useGetSprints(project.key);

  const renderContent = (): ReactNode => {
    if (!project.isLinkedToJira) {
      return (
        <DSEmptyState
          title={t("withoutJira.title")}
          description={t("withoutJira.description")}
          icon="sprints"
        />
      );
    }

    if (isPending) {
      return (
        <div aria-busy="true">
          <DSSkeleton lineCount={6} />
        </div>
      );
    }

    if (isError || data === undefined) {
      return (
        <DSErrorState
          title={t("loadError")}
          retryLabel={t("retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (data.length === 0) {
      return (
        <DSEmptyState
          title={t("empty.title")}
          description={t("empty.description")}
          icon="sprints"
        />
      );
    }

    return <SprintTable projectKey={project.key} sprints={data} />;
  };

  return (
    <>
      <DSPageHeader
        title={t("title")}
        description={t("description")}
        actions={project.isLinkedToJira ? <SyncControl /> : undefined}
      />
      {renderContent()}
    </>
  );
};
