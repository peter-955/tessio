"use client";

import { DSBarChart, DSCard, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useLabelExecutor } from "../../hooks/use-label-executor";
import { CATEGORY_KEY } from "../../typing/constants/insights.constant";
import type { TrendPoint } from "../../typing/types/insights.type";
import { buildExecutorData, buildExecutorSeries } from "../../utils/trend-chart.util";

interface Props {
  points: TrendPoint[];
  executors: string[];
  axisLabel: string;
  labelPoint: (point: TrendPoint) => string;
}

export const ExecutorRunsChart: FC<Props> = ({ points, executors, axisLabel, labelPoint }) => {
  const { t } = useTranslation("insights");
  const labelExecutor = useLabelExecutor();

  return (
    <DSCard title={t("executors.title")}>
      {executors.length === 0 ? (
        <DSText color="muted">{t("executors.empty")}</DSText>
      ) : (
        <DSBarChart
          label={t("executors.title")}
          data={buildExecutorData(points, executors, labelPoint)}
          xKey={CATEGORY_KEY}
          xLabel={axisLabel}
          series={buildExecutorSeries(executors, labelExecutor)}
          isStacked
        />
      )}
    </DSCard>
  );
};
