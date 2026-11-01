"use client";

import { DSSkeleton } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import {
  NOTIFICATION_SKELETON_ICON_SIZE,
  NOTIFICATION_SKELETON_ROW_INDEXES,
} from "../../typing/constants/notification.constant";
import styles from "./notification-list-skeleton.module.scss";

export const NotificationListSkeleton: FC = () => {
  const { t } = useTranslation("notifications");

  return (
    <div role="status" aria-busy="true" aria-label={t("panel.loading")} className={styles.list}>
      {NOTIFICATION_SKELETON_ROW_INDEXES.map((rowIndex) => {
        return (
          <div key={rowIndex} className={styles.row}>
            <DSSkeleton isCircle height={NOTIFICATION_SKELETON_ICON_SIZE} />
            <div className={styles.lines}>
              <DSSkeleton lineCount={2} />
            </div>
          </div>
        );
      })}
    </div>
  );
};
