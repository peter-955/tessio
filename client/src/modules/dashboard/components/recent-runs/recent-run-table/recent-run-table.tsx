"use client";

import { DSBadge, DSTable, DSText } from "@/components/design-system";
import { checkIsUntargetedRun } from "@/modules/runs/utils/run-target.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { RUN_STATUS_COLORS } from "../../../typing/constants/dashboard.constant";
import type { RecentRun } from "../../../typing/types/recent-run.type";
import { buildRunHref } from "../../../utils/dashboard-path.util";
import styles from "./recent-run-table.module.scss";

interface Props {
  projectKey: string;
  runs: RecentRun[];
}

export const RecentRunTable: FC<Props> = ({ projectKey, runs }) => {
  const { t } = useTranslation("dashboard");
  const { t: tSuites } = useTranslation("suites");
  const { t: tJunitImport } = useTranslation("junitImport");
  const formatDate = useFormatDate();

  return (
    <DSTable label={t("recentRuns.title")}>
      <thead>
        <tr>
          <th scope="col">{t("recentRuns.columns.status")}</th>
          <th scope="col">{t("recentRuns.columns.story")}</th>
          <th scope="col">{t("recentRuns.columns.executor")}</th>
          <th scope="col">{t("recentRuns.columns.environment")}</th>
          <th scope="col">{t("recentRuns.columns.startedBy")}</th>
          <th scope="col">{t("recentRuns.columns.startedAt")}</th>
          <th scope="col">{t("recentRuns.columns.results")}</th>
        </tr>
      </thead>
      <tbody>
        {runs.map((run) => {
          return (
            <tr key={run.id}>
              <td>
                <span className={styles.status}>
                  <DSBadge color={RUN_STATUS_COLORS[run.status]}>
                    {t(`recentRuns.status.${run.status}`)}
                  </DSBadge>
                  {run.status === "aborted" && run.abortReason !== null && (
                    <DSText size="xs" color="muted" component="span">
                      {t(`recentRuns.abortReason.${run.abortReason}`)}
                    </DSText>
                  )}
                </span>
              </td>
              <td>
                <span className={styles.story}>
                  <Link href={buildRunHref(projectKey, run.id)}>
                    {run.storyJiraKey ?? run.testSuiteName ?? tJunitImport("ciRun.target")}
                  </Link>
                  <span className={styles.storyTitle}>
                    {run.storyTitle ??
                      (checkIsUntargetedRun(run) ? null : tSuites("runs.suiteBadge"))}
                  </span>
                </span>
              </td>
              <td>{t(`recentRuns.executor.${run.executor}`)}</td>
              <td>{run.environmentName}</td>
              <td>{run.startedByName}</td>
              <td>{formatDate(run.startedAt)}</td>
              <td className={styles.numeric}>
                {t("recentRuns.results", {
                  passed: run.counts.passed,
                  failed: run.counts.failed,
                  total: run.counts.total,
                })}
              </td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
