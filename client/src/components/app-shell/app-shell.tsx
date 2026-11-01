"use client";

import { DSDrawer } from "@/components/design-system";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import styles from "./app-shell.module.scss";
import { Sidebar } from "./sidebar/sidebar";
import { TopBar } from "./top-bar/top-bar";
import { MAIN_CONTENT_ID } from "./typing/constants/app-shell.constant";

interface Props {
  children: ReactNode;
}

export const AppShell: FC<Props> = ({ children }) => {
  const { t } = useTranslation();
  const [isNavigationOpened, setIsNavigationOpened] = useState(false);

  const openNavigation = (): void => {
    setIsNavigationOpened(true);
  };

  const closeNavigation = (): void => {
    setIsNavigationOpened(false);
  };

  return (
    <div className={styles.shell}>
      <a href={`#${MAIN_CONTENT_ID}`} className={styles.skipLink}>
        {t("appShell.skipToContent")}
      </a>
      <aside className={styles.sidebar}>
        <Sidebar />
      </aside>
      <div className={styles.column}>
        <TopBar onOpenNavigation={openNavigation} />
        <main id={MAIN_CONTENT_ID} tabIndex={-1} className={styles.main}>
          {children}
        </main>
      </div>
      <DSDrawer
        isOpened={isNavigationOpened}
        onClose={closeNavigation}
        position="left"
        size="sm"
        title={t("appShell.navigationLabel")}
        closeLabel={t("appShell.closeNavigation")}
      >
        <Sidebar onNavigate={closeNavigation} />
      </DSDrawer>
    </div>
  );
};
