"use client";

import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useInsightFormatters } from "../../hooks/use-insight-formatters";
import type { TrendPoint } from "../../typing/types/insights.type";
import { toPercent } from "../../utils/insight-number.util";
import { InsightStatList } from "../insight-stat-list/insight-stat-list";

interface Props {
  total: TrendPoint;
}

export const TrendSummary: FC<Props> = ({ total }) => {
  const { t } = useTranslation("insights");
  const { formatCount, formatPercent, formatDuration } = useInsightFormatters();
  const passRate = toPercent(total.passRate);

  return (
    <InsightStatList
      stats={[
        {
          key: "passRate",
          label: t("summary.passRate"),
          value: passRate === null ? t("noValue") : formatPercent(passRate),
        },
        { key: "runs", label: t("summary.runs"), value: formatCount(total.runCount) },
        {
          key: "results",
          label: t("summary.results"),
          value: t("summary.resultsValue", {
            passed: total.passedCount,
            failed: total.failedCount,
            blocked: total.blockedCount,
          }),
        },
        {
          key: "failuresOpened",
          label: t("summary.failuresOpened"),
          value: formatCount(total.failuresOpened),
        },
        {
          key: "failuresFixed",
          label: t("summary.failuresFixed"),
          value: formatCount(total.failuresFixed),
        },
        {
          key: "meanTimeToFix",
          label: t("summary.meanTimeToFix"),
          value: formatDuration(total.meanTimeToFixSeconds),
        },
        {
          key: "openGaps",
          label: t("summary.openGaps"),
          value: formatCount(total.openGapCount),
        },
        {
          key: "medianOpenGapAge",
          label: t("summary.medianOpenGapAge"),
          value: formatDuration(total.medianOpenGapAgeSeconds),
        },
      ]}
    />
  );
};
