"use client";

import { DSActionIcon, DSBadge, DSDrawer } from "@/components/design-system";
import { useCallback, useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetUnreadNotificationCount } from "../../hooks/queries/use-get-unread-notification-count";
import { formatUnreadCount } from "../../utils/unread-count.util";
import { NotificationPanel } from "../notification-panel/notification-panel";
import styles from "./notification-bell.module.scss";

export const NotificationBell: FC = () => {
  const { t } = useTranslation("notifications");
  const { unreadCount } = useGetUnreadNotificationCount();
  const [isOpened, setIsOpened] = useState(false);
  const hasUnread = unreadCount > 0;

  const close = useCallback((): void => {
    setIsOpened(false);
  }, []);

  return (
    <>
      <span className={styles.bell}>
        <DSActionIcon
          icon="bell"
          ariaLabel={hasUnread ? t("bell.labelWithCount", { count: unreadCount }) : t("bell.label")}
          aria-haspopup="dialog"
          onClick={() => {
            setIsOpened(true);
          }}
        />
        {hasUnread && (
          <span className={styles.count} aria-hidden="true">
            <DSBadge color="red">{formatUnreadCount(unreadCount)}</DSBadge>
          </span>
        )}
      </span>
      <DSDrawer
        isOpened={isOpened}
        onClose={close}
        position="right"
        size="sm"
        title={t("panel.title")}
        closeLabel={t("panel.close")}
      >
        <NotificationPanel isOpened={isOpened} onNavigate={close} />
      </DSDrawer>
    </>
  );
};
