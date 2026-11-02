"use client";

import { DSBadge, DSTable } from "@/components/design-system";
import type { Project } from "@/components/project-context/typing/types/project.type";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ArchiveMode } from "../../typing/types/archive-mode.type";
import { buildProjectPath } from "../../utils/project-path.util";
import { ProjectActionsMenu } from "./project-actions-menu/project-actions-menu";
import styles from "./projects-table.module.scss";

interface Props {
  projects: Project[];
  isWorkspaceAdmin: boolean;
  onArchiveChange: (project: Project, mode: ArchiveMode) => void;
}

export const ProjectsTable: FC<Props> = ({ projects, isWorkspaceAdmin, onArchiveChange }) => {
  const { t } = useTranslation("projects");

  return (
    <DSTable label={t("list.title")}>
      <thead>
        <tr>
          <th scope="col">{t("list.columns.name")}</th>
          <th scope="col">{t("list.columns.key")}</th>
          <th scope="col">{t("list.columns.jira")}</th>
          <th scope="col">{t("list.columns.role")}</th>
          <th scope="col">{t("list.columns.status")}</th>
          <th scope="col">
            <span className={styles.visuallyHidden}>{t("list.columns.actions")}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        {projects.map((project) => {
          return (
            <tr key={project.id}>
              <td>
                <div className={styles.nameCell}>
                  <Link href={buildProjectPath(project.key)}>{project.name}</Link>
                  {project.description && (
                    <span className={styles.description}>{project.description}</span>
                  )}
                </div>
              </td>
              <td className={styles.mono}>{project.key}</td>
              <td className={styles.mono}>{project.jiraProjectKey ?? t("table.withoutJira")}</td>
              <td>
                {project.myRole ? (
                  <DSBadge color="tessio">{t(`roles.${project.myRole}`)}</DSBadge>
                ) : (
                  <span className={styles.muted}>{t("list.noRole")}</span>
                )}
              </td>
              <td>{project.isArchived && <DSBadge>{t("list.archived")}</DSBadge>}</td>
              <td className={styles.actionsCell}>
                <ProjectActionsMenu
                  project={project}
                  isWorkspaceAdmin={isWorkspaceAdmin}
                  onArchiveChange={onArchiveChange}
                />
              </td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
