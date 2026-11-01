"use client";

import { DSActionIcon, DSIcon, DSText } from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import classNames from "classnames";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePutNotificationRead } from "../../hooks/mutations/use-put-notification-read";
import { useDescribeNotification } from "../../hooks/use-describe-notification";
import { useFormatRelativeTime } from "../../hooks/use-format-relative-time";
import {
  NOTIFICATION_KIND_ICON_SIZE,
  NOTIFICATION_KIND_ICONS,
} from "../../typing/constants/notification.constant";
import type { Notification } from "../../typing/types/notification.type";
import { buildNotificationHref } from "../../utils/notification-href.util";
import styles from "./notification-item.module.scss";

interface Props {
  notification: Notification;
  onNavigate: () => void;
}

export const NotificationItem: FC<Props> = ({ notification, onNavigate }) => {
  const { t } = useTranslation("notifications");
  const describeNotification = useDescribeNotification();
  const formatRelativeTime = useFormatRelativeTime();
  const formatDate = useFormatDate();
  const { mutate: markRead } = usePutNotificationRead();
  const { title, description } = describeNotification(notification);
  const isUnread = !notification.isRead;

  const markAsRead = (): void => {
    markRead(notification.id);
  };

  return (
    <li className={classNames(styles.item, { [styles.unread]: isUnread })}>
      <span className={styles.kind} aria-hidden="true">
        <DSIcon
          name={NOTIFICATION_KIND_ICONS[notification.kind]}
          size={NOTIFICATION_KIND_ICON_SIZE}
        />
        {isUnread && <span className={styles.dot} />}
      </span>
      <div className={styles.content}>
        <Link
          href={buildNotificationHref(notification)}
          prefetch={false}
          className={styles.link}
          onClick={() => {
            if (isUnread) {
              markAsRead();
            }
          }}
          onNavigate={() => {
            onNavigate();
          }}
        >
          {isUnread && <span className={styles.visuallyHidden}>{t("item.unread")}</span>}{" "}
          <DSText
            component="span"
            weight={isUnread ? "medium" : "regular"}
            className={styles.title}
          >
            {title}
          </DSText>{" "}
          {description !== "" && (
            <DSText component="span" size="sm" color="muted" className={styles.description}>
              {description}
            </DSText>
          )}
        </Link>
        <DSText size="xs" color="muted" className={styles.meta}>
          <span>{notification.projectName}</span>
          {notification.actorName !== null && (
            <span>{t("item.byActor", { actorName: notification.actorName })}</span>
          )}
          <time dateTime={notification.createdAt} title={formatDate(notification.createdAt)}>
            {formatRelativeTime(notification.createdAt)}
          </time>
        </DSText>
      </div>
      <div className={styles.action}>
        {isUnread && (
          <DSActionIcon
            icon="check"
            size="sm"
            ariaLabel={t("item.markRead")}
            hasTooltip
            onClick={markAsRead}
          />
        )}
      </div>
    </li>
  );
};
