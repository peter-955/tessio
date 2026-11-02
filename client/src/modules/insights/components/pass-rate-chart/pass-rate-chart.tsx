"use client";

import { DSCard, DSLineChart } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useInsightFormatters } from "../../hooks/use-insight-formatters";
import { CATEGORY_KEY } from "../../typing/constants/insights.constant";
import type { TrendPoint } from "../../typing/types/insights.type";
import { buildPassRateData } from "../../utils/trend-chart.util";

interface Props {
  points: TrendPoint[];
  axisLabel: string;
  labelPoint: (point: TrendPoint) => string;
}

export const PassRateChart: FC<Props> = ({ points, axisLabel, labelPoint }) => {
  const { t } = useTranslation("insights");
  const { formatPercent } = useInsightFormatters();

  return (
    <DSCard title={t("passRate.title")}>
      <DSLineChart
        label={t("passRate.title")}
        data={buildPassRateData(points, labelPoint)}
        xKey={CATEGORY_KEY}
        xLabel={axisLabel}
        series={[{ key: "passRate", label: t("passRate.series"), color: "series1" }]}
        valueFormatter={formatPercent}
      />
    </DSCard>
  );
};
