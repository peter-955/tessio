"use client";

import { DSCard, DSLineChart, DSStack, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useInsightFormatters } from "../../hooks/use-insight-formatters";
import { CATEGORY_KEY } from "../../typing/constants/insights.constant";
import type { TrendPoint } from "../../typing/types/insights.type";
import { buildGapAgeData } from "../../utils/trend-chart.util";

interface Props {
  points: TrendPoint[];
  total: TrendPoint;
  axisLabel: string;
  labelPoint: (point: TrendPoint) => string;
}

export const GapAgeChart: FC<Props> = ({ points, total, axisLabel, labelPoint }) => {
  const { t } = useTranslation("insights");
  const { formatDays, formatDuration } = useInsightFormatters();

  return (
    <DSCard title={t("gaps.title")}>
      <DSStack gap={2}>
        <DSText size="sm" color="muted">
          {t("gaps.summary", {
            opened: total.gapsOpened,
            answered: total.gapsAnswered,
            duration: formatDuration(total.meanGapAnswerSeconds),
          })}
        </DSText>
        <DSLineChart
          label={t("gaps.title")}
          data={buildGapAgeData(points, labelPoint)}
          xKey={CATEGORY_KEY}
          xLabel={axisLabel}
          series={[
            { key: "medianOpenAge", label: t("gaps.medianOpenAge"), color: "series1" },
            { key: "meanAnswer", label: t("gaps.meanAnswer"), color: "series2" },
          ]}
          valueFormatter={formatDays}
        />
      </DSStack>
    </DSCard>
  );
};
