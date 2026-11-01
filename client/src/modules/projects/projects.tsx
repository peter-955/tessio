"use client";

import {
  DSButtonLink,
  DSEmptyState,
  DSErrorState,
  DSPageHeader,
  DSStack,
  DSSwitch,
} from "@/components/design-system";
import type { Project } from "@/components/project-context/typing/types/project.type";
import { useGetProjects } from "@/shared/hooks/queries/use-get-projects";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { ArchiveProjectModal } from "./components/archive-project-modal/archive-project-modal";
import { LoadingState } from "./components/loading-state/loading-state";
import { ProjectsTable } from "./components/projects-table/projects-table";
import { useIsWorkspaceAdmin } from "./hooks/use-is-workspace-admin";
import { NEW_PROJECT_PATH } from "./typing/constants/project-path.constant";
import type { ArchiveMode } from "./typing/types/archive-mode.type";
import type { ArchiveTarget } from "./typing/types/archive-target.type";

export const ProjectsPage: FC = () => {
  const { t } = useTranslation("projects");
  const isWorkspaceAdmin = useIsWorkspaceAdmin();
  const [isIncludingArchived, setIsIncludingArchived] = useState(false);
  const [archiveTarget, setArchiveTarget] = useState<ArchiveTarget | null>(null);
  const [isArchiveModalOpened, setIsArchiveModalOpened] = useState(false);
  const { data: projects, isPending, isError, refetch } = useGetProjects({ isIncludingArchived });

  const handleArchiveChange = (project: Project, mode: ArchiveMode): void => {
    setArchiveTarget({ project, mode });
    setIsArchiveModalOpened(true);
  };

  const handleArchiveModalClose = (): void => {
    setIsArchiveModalOpened(false);
  };

  const renderContent = (): ReactNode => {
    if (isPending) {
      return <LoadingState label={t("list.loading")} />;
    }

    if (isError || projects === undefined) {
      return (
        <DSErrorState
          title={t("list.loadError")}
          retryLabel={t("errors.retry")}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (projects.length === 0) {
      return isWorkspaceAdmin ? (
        <DSEmptyState
          title={t("list.empty.adminTitle")}
          icon="projects"
          action={
            <DSButtonLink href={NEW_PROJECT_PATH} type="primary" icon="plus">
              {t("list.newProject")}
            </DSButtonLink>
          }
        />
      ) : (
        <DSEmptyState
          title={t("list.empty.memberTitle")}
          description={t("list.empty.memberDescription")}
          icon="projects"
        />
      );
    }

    return (
      <ProjectsTable
        projects={projects}
        isWorkspaceAdmin={isWorkspaceAdmin}
        onArchiveChange={handleArchiveChange}
      />
    );
  };

  return (
    <>
      <DSPageHeader
        title={t("list.title")}
        description={t("list.description")}
        actions={
          isWorkspaceAdmin && (
            <DSButtonLink href={NEW_PROJECT_PATH} type="primary" icon="plus">
              {t("list.newProject")}
            </DSButtonLink>
          )
        }
      />
      <DSStack gap={4}>
        <DSSwitch
          label={t("list.showArchived")}
          isChecked={isIncludingArchived}
          onChange={setIsIncludingArchived}
        />
        {renderContent()}
      </DSStack>
      <ArchiveProjectModal
        target={archiveTarget}
        isOpened={isArchiveModalOpened}
        onClose={handleArchiveModalClose}
      />
    </>
  );
};
