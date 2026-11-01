"use client";

import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { Notification } from "../../typing/types/notification.type";
import { NotificationItem } from "../notification-item/notification-item";
import styles from "./notification-list.module.scss";

interface Props {
  notifications: Notification[];
  onNavigate: () => void;
}

export const NotificationList: FC<Props> = ({ notifications, onNavigate }) => {
  const { t } = useTranslation("notifications");

  return (
    <ul className={styles.list} aria-label={t("panel.title")}>
      {notifications.map((notification) => {
        return (
          <NotificationItem
            key={notification.id}
            notification={notification}
            onNavigate={onNavigate}
          />
        );
      })}
    </ul>
  );
};
