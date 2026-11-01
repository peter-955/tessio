"use client";

import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { useParams, usePathname } from "next/navigation";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { WORKSPACE_NAVIGATION_ITEMS } from "../../typing/constants/navigation.constant";
import { checkIsActiveRoute } from "../../utils/navigation.util";
import { checkIsWorkspaceAdmin } from "../../utils/workspace-role.util";
import { NavigationLink } from "../navigation-link/navigation-link";
import styles from "./workspace-navigation.module.scss";

interface Props {
  onNavigate?: () => void;
}

export const WorkspaceNavigation: FC<Props> = ({ onNavigate }) => {
  const { t } = useTranslation();
  const { t: translateNavigation } = useTranslation("navigation");
  const pathname = usePathname();
  const { projectKey } = useParams<{ projectKey?: string }>();
  const currentUser = useCurrentUser();
  const isWorkspaceAdmin = checkIsWorkspaceAdmin(currentUser.workspaceRole);
  const isInsideProject = typeof projectKey === "string";
  const visibleItems = WORKSPACE_NAVIGATION_ITEMS.filter((item) => {
    return !item.isWorkspaceAdminOnly || isWorkspaceAdmin;
  });

  return (
    <nav aria-label={t("appShell.workspaceNavigation")} className={styles.navigation}>
      {visibleItems.map((item) => {
        return (
          <NavigationLink
            key={item.href}
            href={item.href}
            icon={item.icon}
            label={translateNavigation(item.labelKey)}
            isActive={!isInsideProject && checkIsActiveRoute(pathname, item.href, false)}
            onNavigate={onNavigate}
          />
        );
      })}
    </nav>
  );
};
