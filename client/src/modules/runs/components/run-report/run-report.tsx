"use client";

import { DSCard, DSStack, DSText } from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import type { RunReport as RunReportData } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { listCountEntries } from "../../utils/run-counts.util";
import { ReportCriteria } from "./report-criteria/report-criteria";
import { ReportFailedCases } from "./report-failed-cases/report-failed-cases";
import { ReportMissingScreenshots } from "./report-missing-screenshots/report-missing-screenshots";
import styles from "./run-report.module.scss";

interface Props {
  projectKey: string;
  runId: string;
  report: RunReportData;
}

export const RunReport: FC<Props> = ({ projectKey, runId, report }) => {
  const { t } = useTranslation("runs");
  const formatDate = useFormatDate();
  const countText = [
    t("counts.total", { count: report.counts.total }),
    ...listCountEntries(report.counts).map((entry) => {
      return t(`counts.${entry.key}`, { count: entry.count });
    }),
  ].join(" · ");

  return (
    <DSStack gap={4}>
      <DSCard title={t("report.summary")}>
        <DSStack gap={2}>
          {report.summary === null ? (
            <DSText color="muted">{t("report.noSummary")}</DSText>
          ) : (
            <DSText className={styles.summary}>{report.summary}</DSText>
          )}
          <DSText size="sm">{countText}</DSText>
          <DSText size="xs" color="muted">
            {t("report.builtAt", { time: formatDate(report.builtAt) })}
          </DSText>
        </DSStack>
      </DSCard>
      <ReportFailedCases projectKey={projectKey} runId={runId} failedCases={report.failedCases} />
      <ReportCriteria criterionImpacts={report.criterionImpacts} />
      <ReportMissingScreenshots missingScreenshots={report.missingScreenshots} />
    </DSStack>
  );
};
