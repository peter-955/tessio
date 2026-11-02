"use client";

import { DSEmptyState, DSErrorState, DSSkeleton, DSTable } from "@/components/design-system";
import { TestCaseStatusBadge } from "@/modules/test-cases/components/test-case-status-badge/test-case-status-badge";
import { TEST_CASE_STATUSES } from "@/modules/test-cases/typing/constants/test-case.constant";
import type { TestCaseStatus } from "@/modules/test-cases/typing/types/test-case.type";
import { buildTestCasePath } from "@/modules/test-cases/utils/test-case-path.util";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetSharedStepUsage } from "../../hooks/queries/use-get-shared-step-usage";
import { LOADING_ROW_COUNT } from "../../typing/constants/shared-step.constant";
import styles from "./shared-step-usage-list.module.scss";

interface Props {
  projectKey: string;
  sharedStepKey: string;
}

const readStatus = (status: string): TestCaseStatus | null => {
  return TEST_CASE_STATUSES.find((candidate) => candidate === status) ?? null;
};

export const SharedStepUsageList: FC<Props> = ({ projectKey, sharedStepKey }) => {
  const { t } = useTranslation("sharedSteps");
  const { data, isPending, isError, isFetching, refetch } = useGetSharedStepUsage(
    projectKey,
    sharedStepKey,
  );

  if (isPending) {
    return (
      <div role="status" aria-busy="true" aria-label={t("usage.loading")}>
        <DSSkeleton lineCount={LOADING_ROW_COUNT} height={32} />
      </div>
    );
  }

  if (isError || data === undefined) {
    return (
      <DSErrorState
        title={t("usage.loadError")}
        retryLabel={t("usage.retry")}
        isRetrying={isFetching}
        titleOrder={3}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  if (data.length === 0) {
    return (
      <DSEmptyState
        title={t("usage.emptyTitle")}
        description={t("usage.emptyDescription")}
        icon="testCases"
        size="sm"
        titleOrder={3}
      />
    );
  }

  return (
    <DSTable label={t("usage.tableLabel")}>
      <caption className={styles.caption}>{t("usage.tableLabel")}</caption>
      <thead>
        <tr>
          <th scope="col">{t("usage.columns.case")}</th>
          <th scope="col">{t("usage.columns.story")}</th>
          <th scope="col">{t("usage.columns.status")}</th>
        </tr>
      </thead>
      <tbody>
        {data.map((usage) => {
          const status = readStatus(usage.status);

          return (
            <tr key={usage.testCaseId}>
              <td>
                <span className={styles.case}>
                  <Link href={buildTestCasePath(projectKey, usage.code)} className={styles.code}>
                    {usage.code}
                  </Link>
                  <span>{usage.title}</span>
                </span>
              </td>
              <td className={styles.nowrap}>{usage.storyJiraKey}</td>
              <td>{status === null ? usage.status : <TestCaseStatusBadge status={status} />}</td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
