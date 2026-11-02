"use client";

import { DSCard, DSStack, DSText } from "@/components/design-system";
import { UnmappedTestsCard } from "@/modules/junit-import/components/unmapped-tests-card/unmapped-tests-card";
import { RunSkippedCases } from "@/modules/suites/components/run-skipped-cases/run-skipped-cases";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import type { RunReport as RunReportData } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { listCountEntries } from "../../utils/run-counts.util";
import { ReportCriteria } from "./report-criteria/report-criteria";
import { ReportFailedCases } from "./report-failed-cases/report-failed-cases";
import { ReportMissingScreenshots } from "./report-missing-screenshots/report-missing-screenshots";
import { ReportStories } from "./report-stories/report-stories";
import styles from "./run-report.module.scss";

interface Props {
  projectKey: string;
  runId: string;
  report: RunReportData;
  isSuiteRun?: boolean;
}

export const RunReport: FC<Props> = ({ projectKey, runId, report, isSuiteRun = false }) => {
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
      {isSuiteRun && <ReportStories projectKey={projectKey} stories={report.stories ?? []} />}
      <ReportFailedCases
        projectKey={projectKey}
        runId={runId}
        failedCases={report.failedCases}
        isStoryShown={isSuiteRun}
      />
      <UnmappedTestsCard tests={report.unmappedTests ?? []} totalCount={report.unmappedTestCount} />
      <ReportCriteria criterionImpacts={report.criterionImpacts} />
      <ReportMissingScreenshots missingScreenshots={report.missingScreenshots} />
      {isSuiteRun && (
        <RunSkippedCases projectKey={projectKey} skippedCases={report.skippedCases ?? []} />
      )}
    </DSStack>
  );
};
