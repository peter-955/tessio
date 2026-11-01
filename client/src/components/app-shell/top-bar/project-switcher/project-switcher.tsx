"use client";

import { DSBadge, DSIcon, DSMenu, type DSMenuItem } from "@/components/design-system";
import type { Project } from "@/components/project-context/typing/types/project.type";
import { useGetProject } from "@/shared/hooks/queries/use-get-project";
import { useGetProjects } from "@/shared/hooks/queries/use-get-projects";
import { usePathname } from "next/navigation";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useActiveProjectKey } from "../../hooks/use-active-project-key";
import { buildProjectSwitchHref } from "../../utils/navigation.util";
import styles from "./project-switcher.module.scss";

export const ProjectSwitcher: FC = () => {
  const { t } = useTranslation();
  const pathname = usePathname();
  const activeProjectKey = useActiveProjectKey();
  const { data: currentProject } = useGetProject(activeProjectKey);
  const { data: projects, isPending, isError } = useGetProjects();
  const activeProjects = (projects ?? []).filter((project) => {
    return !project.isArchived;
  });

  const buildProjectItem = (project: Project): DSMenuItem => {
    const isCurrent = project.key === activeProjectKey;
    return {
      key: project.id,
      label: `${project.name} (${project.key})`,
      href: buildProjectSwitchHref(pathname, activeProjectKey, project),
      icon: isCurrent ? "check" : undefined,
      isCurrent,
    };
  };

  const buildProjectItems = (): DSMenuItem[] => {
    if (isPending) {
      return [{ key: "loading", label: t("appShell.projectSwitcher.loading"), isDisabled: true }];
    }
    if (isError) {
      return [
        { key: "loadError", label: t("appShell.projectSwitcher.loadError"), isDisabled: true },
      ];
    }
    if (activeProjects.length === 0) {
      return [{ key: "empty", label: t("appShell.projectSwitcher.empty"), isDisabled: true }];
    }
    return activeProjects.map(buildProjectItem);
  };

  const items: DSMenuItem[] = [
    { key: "listLabel", type: "label", label: t("appShell.projectSwitcher.listLabel") },
    ...buildProjectItems(),
    { key: "divider", type: "divider" },
    {
      key: "allProjects",
      label: t("appShell.projectSwitcher.allProjects"),
      href: "/projects",
      icon: "projects",
    },
  ];

  return (
    <DSMenu
      width={280}
      position="bottom-start"
      items={items}
      target={
        <button type="button" className={styles.target}>
          {currentProject ? (
            <>
              <span className={styles.visuallyHidden}>
                {t("appShell.projectSwitcher.currentPrefix")}
              </span>{" "}
              <span className={styles.name}>{currentProject.name}</span>{" "}
              <span className={styles.key}>{currentProject.key}</span>{" "}
              {currentProject.isArchived && (
                <DSBadge color="yellow">{t("appShell.projectSwitcher.archived")}</DSBadge>
              )}
            </>
          ) : (
            <span className={styles.placeholder}>{t("appShell.projectSwitcher.placeholder")}</span>
          )}
          <span className={styles.icon}>
            <DSIcon name="selector" size={16} />
          </span>
        </button>
      }
    />
  );
};
