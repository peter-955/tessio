"use client";

import { DSCard, DSText } from "@/components/design-system";
import { StatusBadge } from "@/components/status-badge/status-badge";
import { SuspectedCause } from "@/components/suspected-cause/suspected-cause";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { RunDetailTab } from "../../../typing/enums/run-detail-tab.enum";
import type { FailedCaseReport } from "../../../typing/types/run.type";
import { buildRunPath } from "../../../utils/run-path.util";
import styles from "./report-failed-cases.module.scss";

interface Props {
  projectKey: string;
  runId: string;
  failedCases: FailedCaseReport[];
  isStoryShown?: boolean;
}

export const ReportFailedCases: FC<Props> = ({
  projectKey,
  runId,
  failedCases,
  isStoryShown = false,
}) => {
  const { t } = useTranslation("runs");
  const resultsPath = buildRunPath(projectKey, runId, RunDetailTab.RESULTS);

  return (
    <DSCard title={t("report.failedCases")}>
      {failedCases.length === 0 ? (
        <DSText color="muted">{t("report.noFailures")}</DSText>
      ) : (
        <ul className={styles.list}>
          {failedCases.map((failedCase) => {
            return (
              <li key={failedCase.testCaseId} className={styles.item}>
                <div className={styles.header}>
                  <Link href={`${resultsPath}#case-${failedCase.code}`} className={styles.code}>
                    {failedCase.code}
                  </Link>
                  <DSText weight="medium" component="span" className={styles.wrapping}>
                    {failedCase.title}
                  </DSText>
                  {isStoryShown && (failedCase.storyJiraKey ?? null) !== null && (
                    <DSText size="sm" color="muted" component="span">
                      {failedCase.storyJiraKey}
                    </DSText>
                  )}
                  <StatusBadge status={failedCase.status} />
                </div>
                {failedCase.suspectedCause !== null && failedCase.suspectedCause !== undefined && (
                  <SuspectedCause
                    cause={failedCase.suspectedCause}
                    reason={failedCase.causeReason ?? null}
                  />
                )}
                {failedCase.stepOrder !== null && (
                  <DSText size="sm" className={styles.wrapping}>
                    {t("report.failedStep", {
                      order: failedCase.stepOrder,
                      action: failedCase.stepAction ?? "",
                    })}
                  </DSText>
                )}
                {failedCase.actualResult !== null && (
                  <DSText size="sm" color="muted" className={styles.preformatted}>
                    {failedCase.actualResult}
                  </DSText>
                )}
                {failedCase.error !== null && (
                  <DSText size="sm" className={`${styles.preformatted} ${styles.error}`}>
                    {failedCase.error}
                  </DSText>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </DSCard>
  );
};
