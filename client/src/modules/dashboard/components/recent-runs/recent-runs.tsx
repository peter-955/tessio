"use client";

import {
  DSEmptyState,
  DSErrorState,
  DSSkeleton,
  DSStack,
  DSTitle,
} from "@/components/design-system";
import Link from "next/link";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetRecentRuns } from "../../hooks/queries/use-get-recent-runs";
import { buildRunsHref } from "../../utils/dashboard-path.util";
import { RecentRunTable } from "./recent-run-table/recent-run-table";
import styles from "./recent-runs.module.scss";

interface Props {
  projectKey: string;
}

export const RecentRuns: FC<Props> = ({ projectKey }) => {
  const { t } = useTranslation("dashboard");
  const { data, isPending, isError, isFetching, refetch } = useGetRecentRuns(projectKey);

  const renderContent = (): ReactNode => {
    if (isPending) {
      return (
        <div aria-busy="true">
          <DSSkeleton lineCount={5} />
        </div>
      );
    }

    if (isError || data === undefined) {
      return (
        <DSErrorState
          title={t("recentRuns.loadError")}
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
          title={t("recentRuns.empty.title")}
          description={t("recentRuns.empty.description")}
          icon="runs"
          size="sm"
        />
      );
    }

    return <RecentRunTable projectKey={projectKey} runs={data} />;
  };

  return (
    <section>
      <DSStack gap={3}>
        <div className={styles.header}>
          <DSTitle order={2} type="section">
            {t("recentRuns.title")}
          </DSTitle>
          <Link href={buildRunsHref(projectKey)} className={styles.viewAll}>
            {t("recentRuns.viewAll")}
          </Link>
        </div>
        {renderContent()}
      </DSStack>
    </section>
  );
};
