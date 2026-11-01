"use client";

import {
  DSButton,
  DSEmptyState,
  DSErrorState,
  DSGroup,
  DSSegmentedControl,
  DSStack,
  type DSSegmentedOption,
} from "@/components/design-system";
import { useMemo, useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { usePutAllNotificationsRead } from "../../hooks/mutations/use-put-all-notifications-read";
import { useGetNotifications } from "../../hooks/queries/use-get-notifications";
import { useGetUnreadNotificationCount } from "../../hooks/queries/use-get-unread-notification-count";
import { NOTIFICATION_FILTERS } from "../../typing/constants/notification.constant";
import type { NotificationFilter } from "../../typing/types/notification.type";
import { NotificationListSkeleton } from "../notification-list-skeleton/notification-list-skeleton";
import { NotificationList } from "../notification-list/notification-list";
import styles from "./notification-panel.module.scss";

interface Props {
  isOpened: boolean;
  onNavigate: () => void;
}

export const NotificationPanel: FC<Props> = ({ isOpened, onNavigate }) => {
  const { t } = useTranslation("notifications");
  const [filter, setFilter] = useState<NotificationFilter>("all");
  const isUnreadOnly = filter === "unread";
  const {
    notifications,
    isPending,
    isError,
    refetch,
    isRefetching,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  } = useGetNotifications({ isUnreadOnly, isEnabled: isOpened });
  const { unreadCount } = useGetUnreadNotificationCount();
  const { mutate: markAllRead, isPending: isMarkingAllRead } = usePutAllNotificationsRead();

  const filterOptions = useMemo((): DSSegmentedOption<NotificationFilter>[] => {
    const labels: Record<NotificationFilter, string> = {
      all: t("panel.filterAll"),
      unread: t("panel.filterUnread"),
    };

    return NOTIFICATION_FILTERS.map((option) => {
      return { value: option, label: labels[option] };
    });
  }, [t]);

  const renderContent = (): ReactNode => {
    if (isPending) {
      return <NotificationListSkeleton />;
    }

    if (isError) {
      return (
        <DSErrorState
          title={t("error.title")}
          retryLabel={t("error.retry")}
          isRetrying={isRefetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (notifications.length === 0) {
      return (
        <DSEmptyState
          icon="inbox"
          title={isUnreadOnly ? t("empty.unreadTitle") : t("empty.allTitle")}
          description={isUnreadOnly ? t("empty.unreadDescription") : t("empty.allDescription")}
        />
      );
    }

    return (
      <DSStack gap={3}>
        <NotificationList notifications={notifications} onNavigate={onNavigate} />
        {hasNextPage && (
          <DSButton
            type="default"
            isFullWidth
            isLoading={isFetchingNextPage}
            onClick={() => {
              void fetchNextPage();
            }}
          >
            {t("panel.loadMore")}
          </DSButton>
        )}
      </DSStack>
    );
  };

  return (
    <DSStack gap={4} className={styles.panel}>
      <DSGroup justify="between" gap={2} isWrapping>
        <DSSegmentedControl
          value={filter}
          options={filterOptions}
          onChange={setFilter}
          ariaLabel={t("panel.filterLabel")}
        />
        <DSButton
          type="ghost"
          size="sm"
          icon="check"
          isDisabled={unreadCount === 0}
          isLoading={isMarkingAllRead}
          onClick={() => {
            markAllRead();
          }}
        >
          {t("panel.markAllRead")}
        </DSButton>
      </DSGroup>
      {renderContent()}
    </DSStack>
  );
};
