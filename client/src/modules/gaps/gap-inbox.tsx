"use client";

import {
  DSEmptyState,
  DSErrorState,
  DSPageHeader,
  DSSegmentedControl,
  DSStack,
  DSText,
  type DSSegmentedOption,
} from "@/components/design-system";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { GapListSkeleton } from "./components/gap-list-skeleton/gap-list-skeleton";
import { GapList } from "./components/gap-list/gap-list";
import styles from "./gap-inbox.module.scss";
import { useGetGapInbox } from "./hooks/queries/use-get-gap-inbox";
import {
  INBOX_FILTER_LABEL_KEYS,
  INBOX_FILTERS,
  MAX_INBOX_SIZE,
} from "./typing/constants/gap.constant";
import type { Gap, InboxFilter } from "./typing/types/gap.type";
import { canReopenGap } from "./utils/gap-permission.util";

export const GapInboxPage: FC = () => {
  const { t } = useTranslation("gaps");
  const currentUser = useCurrentUser();
  const [filter, setFilter] = useState<InboxFilter>("open");
  const { data, isPending, isError, isFetching, refetch } = useGetGapInbox(filter === "all");
  const filterOptions = INBOX_FILTERS.map((inboxFilter): DSSegmentedOption<InboxFilter> => {
    return { value: inboxFilter, label: t(INBOX_FILTER_LABEL_KEYS[inboxFilter]) };
  });

  const checkCanReopen = (gap: Gap): boolean => {
    return canReopenGap(gap, currentUser.id, null, true);
  };

  const renderGaps = (): ReactNode => {
    if (isPending) {
      return <GapListSkeleton />;
    }

    if (isError || data === undefined) {
      return (
        <DSErrorState
          title={t("loadError")}
          retryLabel={t("retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (data.length === 0) {
      return (
        <DSEmptyState
          title={t("inbox.emptyTitle")}
          description={t("inbox.emptyDescription")}
          icon="inbox"
        />
      );
    }

    return (
      <DSStack gap={3}>
        <GapList gaps={data} isInboxContext canAnswer canReassign checkCanReopen={checkCanReopen} />
        {data.length >= MAX_INBOX_SIZE && (
          <DSText size="sm" color="muted">
            {t("inbox.limitNotice", { count: MAX_INBOX_SIZE })}
          </DSText>
        )}
      </DSStack>
    );
  };

  return (
    <>
      <DSPageHeader title={t("inbox.title")} description={t("inbox.description")} />
      <DSStack gap={4} className={styles.content}>
        <div className={styles.filter}>
          <DSSegmentedControl<InboxFilter>
            value={filter}
            options={filterOptions}
            onChange={setFilter}
            ariaLabel={t("inbox.filterLabel")}
          />
        </div>
        {renderGaps()}
      </DSStack>
    </>
  );
};
