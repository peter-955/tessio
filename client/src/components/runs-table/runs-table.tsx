"use client";

import { DSTable, DSText } from "@/components/design-system";
import { StatusBadge } from "@/components/status-badge/status-badge";
import { computeRunDuration } from "@/modules/runs/utils/run-duration.util";
import { buildRunPath } from "@/modules/runs/utils/run-path.util";
import { checkIsUntargetedRun } from "@/modules/runs/utils/run-target.util";
import { SuiteRunTarget } from "@/modules/suites/components/suite-run-target/suite-run-target";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useFormatDuration } from "@/shared/hooks/use-format-duration";
import type { RunSummary } from "@/shared/typing/types/test-run.type";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { RunCountsCell } from "./run-counts-cell/run-counts-cell";
import styles from "./runs-table.module.scss";

interface Props {
  runs: RunSummary[];
  projectKey: string;
  isStoryColumnShown: boolean;
}

export const RunsTable: FC<Props> = ({ runs, projectKey, isStoryColumnShown }) => {
  const { t } = useTranslation("runs");
  const { t: tJunitImport } = useTranslation("junitImport");
  const formatDate = useFormatDate();
  const formatDuration = useFormatDuration();

  return (
    <DSTable label={t("table.label")}>
      <caption className={styles.caption}>{t("table.label")}</caption>
      <thead>
        <tr>
          <th scope="col">{t("table.started")}</th>
          {isStoryColumnShown && <th scope="col">{t("table.story")}</th>}
          <th scope="col">{t("table.status")}</th>
          <th scope="col">{t("table.executor")}</th>
          <th scope="col">{t("table.environment")}</th>
          <th scope="col">{t("table.startedBy")}</th>
          <th scope="col">{t("table.results")}</th>
          <th scope="col">{t("table.duration")}</th>
        </tr>
      </thead>
      <tbody>
        {runs.map((run) => {
          const duration = computeRunDuration(run.startedAt, run.finishedAt);
          const storyLabel = `${run.storyJiraKey ?? ""} · ${run.storyTitle ?? ""}`;

          return (
            <tr key={run.id}>
              <td>
                <div className={styles.stacked}>
                  <Link href={buildRunPath(projectKey, run.id)}>{formatDate(run.startedAt)}</Link>
                  {run.parentRunId !== null && (
                    <Link
                      href={buildRunPath(projectKey, run.parentRunId)}
                      className={styles.lineageLink}
                    >
                      {t("lineage.rerunOf")}
                    </Link>
                  )}
                </div>
              </td>
              {isStoryColumnShown && (
                <td>
                  {run.testSuiteId !== undefined &&
                  run.testSuiteId !== null &&
                  run.storyId === null ? (
                    <SuiteRunTarget
                      projectKey={projectKey}
                      suiteId={run.testSuiteId}
                      suiteName={run.testSuiteName ?? run.testSuiteId}
                    />
                  ) : checkIsUntargetedRun(run) ? (
                    <span className={styles.muted}>{tJunitImport("ciRun.target")}</span>
                  ) : (
                    <span className={styles.story} title={storyLabel}>
                      {storyLabel}
                    </span>
                  )}
                </td>
              )}
              <td>
                <div className={styles.stacked}>
                  <StatusBadge status={run.status} />
                  {run.status === "aborted" && run.abortReason !== null && (
                    <DSText size="xs" color="muted" component="span">
                      {t(`abortReason.${run.abortReason}`)}
                    </DSText>
                  )}
                </div>
              </td>
              <td>{t(`executor.${run.executor}`)}</td>
              <td>{run.environmentName}</td>
              <td>{run.startedByName}</td>
              <td>
                <RunCountsCell counts={run.counts} />
              </td>
              <td className={styles.muted}>
                {duration === null ? t("table.running") : formatDuration(duration)}
              </td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
