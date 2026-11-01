"use client";

import { DSActionIcon, DSGroup } from "@/components/design-system";
import { NotificationBell } from "@/modules/notifications/components/notification-bell/notification-bell";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { UserMenu } from "../user-menu/user-menu";
import { ProjectSwitcher } from "./project-switcher/project-switcher";
import { SearchPlaceholder } from "./search-placeholder/search-placeholder";
import styles from "./top-bar.module.scss";

interface Props {
  onOpenNavigation: () => void;
}

export const TopBar: FC<Props> = ({ onOpenNavigation }) => {
  const { t } = useTranslation();

  return (
    <header className={styles.topBar}>
      <DSGroup justify="between" gap={4}>
        <DSGroup gap={2} className={styles.start}>
          <span className={styles.menuButton}>
            <DSActionIcon
              icon="menu"
              ariaLabel={t("appShell.openNavigation")}
              onClick={onOpenNavigation}
            />
          </span>
          <ProjectSwitcher />
        </DSGroup>
        <SearchPlaceholder />
        <DSGroup gap={2}>
          <NotificationBell />
          <UserMenu />
        </DSGroup>
      </DSGroup>
    </header>
  );
};
