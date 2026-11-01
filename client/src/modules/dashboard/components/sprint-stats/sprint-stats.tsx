"use client";

import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { DashboardSummary } from "../../typing/types/dashboard.type";
import { calculateCoveragePercent } from "../../utils/coverage.util";
import { buildSprintStoriesHref } from "../../utils/dashboard-path.util";
import styles from "./sprint-stats.module.scss";

interface Props {
  projectKey: string;
  sprintId: string;
  summary: DashboardSummary;
}

export const SprintStats: FC<Props> = ({ projectKey, sprintId, summary }) => {
  const { t } = useTranslation("dashboard");
  const coveragePercent = calculateCoveragePercent(summary.coverage);

  return (
    <dl className={styles.stats}>
      <div className={styles.tile}>
        <dt className={styles.label}>{t("stats.stories")}</dt>
        <dd className={styles.value}>
          <Link href={buildSprintStoriesHref(projectKey, sprintId, null)} className={styles.link}>
            {summary.storyCount}
          </Link>
        </dd>
      </div>
      <div className={styles.tile}>
        <dt className={styles.label}>{t("stats.openGaps")}</dt>
        <dd className={styles.value}>{summary.openGapCount}</dd>
      </div>
      <div className={styles.tile}>
        <dt className={styles.label}>{t("stats.activeFailures")}</dt>
        <dd className={styles.value}>{summary.activeFailureCount}</dd>
      </div>
      <div className={styles.tile}>
        <dt className={styles.label}>{t("stats.coverage")}</dt>
        <dd className={styles.value}>
          {coveragePercent === null
            ? t("stats.noValue")
            : t("stats.percent", { percent: coveragePercent })}
        </dd>
      </div>
    </dl>
  );
};
