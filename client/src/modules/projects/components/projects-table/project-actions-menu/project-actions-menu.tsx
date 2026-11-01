"use client";

import { DSActionIcon, DSMenu, type DSMenuItem } from "@/components/design-system";
import type { Project } from "@/components/project-context/typing/types/project.type";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ArchiveMode } from "../../../typing/types/archive-mode.type";
import { buildProjectPath } from "../../../utils/project-path.util";

interface Props {
  project: Project;
  isWorkspaceAdmin: boolean;
  onArchiveChange: (project: Project, mode: ArchiveMode) => void;
}

export const ProjectActionsMenu: FC<Props> = ({ project, isWorkspaceAdmin, onArchiveChange }) => {
  const { t } = useTranslation("projects");

  const items: DSMenuItem[] = [
    {
      key: "members",
      label: t("list.actions.members"),
      icon: "members",
      href: buildProjectPath(project.key, "members"),
    },
  ];

  if (checkHasProjectCapability(project, "project.edit")) {
    items.push({
      key: "settings",
      label: t("list.actions.settings"),
      icon: "settings",
      href: buildProjectPath(project.key, "settings"),
    });
  }

  if (isWorkspaceAdmin) {
    items.push({ key: "divider", type: "divider" });
    items.push(
      project.isArchived
        ? {
            key: "unarchive",
            label: t("list.actions.unarchive"),
            icon: "restore",
            onClick: () => {
              onArchiveChange(project, "unarchive");
            },
          }
        : {
            key: "archive",
            label: t("list.actions.archive"),
            icon: "archive",
            isDanger: true,
            onClick: () => {
              onArchiveChange(project, "archive");
            },
          },
    );
  }

  return (
    <DSMenu
      items={items}
      target={<DSActionIcon icon="dots" ariaLabel={t("list.actionsFor", { name: project.name })} />}
    />
  );
};
