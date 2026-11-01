"use client";

import { DSPageHeader } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { MyWorkPanel } from "./components/my-work-panel/my-work-panel";
import { RecentRuns } from "./components/recent-runs/recent-runs";
import { SprintPanel } from "./components/sprint-panel/sprint-panel";
import styles from "./dashboard.module.scss";
import { useDashboardSprintId } from "./hooks/use-dashboard-sprint-id";

interface Props {
  initialSprintId: string | null;
}

export const DashboardPage: FC<Props> = ({ initialSprintId }) => {
  const { t } = useTranslation("dashboard");
  const project = useCurrentProject();
  const { sprintId, changeSprintId } = useDashboardSprintId(initialSprintId);

  return (
    <>
      <DSPageHeader title={t("title")} description={t("description")} />
      <div className={styles.panels}>
        <SprintPanel projectKey={project.key} sprintId={sprintId} onSprintChange={changeSprintId} />
        <MyWorkPanel projectKey={project.key} sprintId={sprintId} />
        <RecentRuns projectKey={project.key} />
      </div>
    </>
  );
};
