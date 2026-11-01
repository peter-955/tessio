"use client";

import { DSErrorState, DSSkeleton } from "@/components/design-system";
import { useGetProject } from "@/shared/hooks/queries/use-get-project";
import { useEffect, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { ProjectContext } from "../contexts/project.context";
import { useLastProjectKey } from "../hooks/use-last-project-key";
import { ArchivedBanner } from "./archived-banner/archived-banner";
import styles from "./project-gate.module.scss";
import { ProjectNotFound } from "./project-not-found/project-not-found";

interface Props {
  projectKey: string;
  children: ReactNode;
}

export const ProjectGate: FC<Props> = ({ projectKey, children }) => {
  const { t } = useTranslation();
  const { t: translateErrors } = useTranslation("errors");
  const { data: project, error, isPending, isFetching, refetch } = useGetProject(projectKey);
  const { rememberProjectKey, forgetProjectKey } = useLastProjectKey();
  const isProjectMissing = error?.status === 404;
  const rememberableProjectKey = project && !project.isArchived ? project.key : null;

  useEffect(() => {
    if (isProjectMissing) {
      forgetProjectKey(projectKey);
    }
  }, [forgetProjectKey, isProjectMissing, projectKey]);

  useEffect(() => {
    if (rememberableProjectKey !== null) {
      rememberProjectKey(rememberableProjectKey);
    }
  }, [rememberProjectKey, rememberableProjectKey]);

  if (isPending) {
    return (
      <div
        className={styles.loading}
        role="status"
        aria-busy="true"
        aria-label={t("appShell.projectLoading")}
      >
        <DSSkeleton height={28} width="40%" />
        <DSSkeleton lineCount={4} />
      </div>
    );
  }

  if (isProjectMissing) {
    return <ProjectNotFound />;
  }

  if (project === undefined) {
    return (
      <DSErrorState
        title={translateErrors("projectLoadFailed.title")}
        retryLabel={translateErrors("boundary.retry")}
        onRetry={() => {
          void refetch();
        }}
        isRetrying={isFetching}
      />
    );
  }

  return (
    <ProjectContext value={project}>
      {project.isArchived && (
        <div className={styles.banner}>
          <ArchivedBanner />
        </div>
      )}
      {children}
    </ProjectContext>
  );
};
